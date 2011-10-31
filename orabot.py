# Copyright 2011 orabot Developers
#
# This file is part of orabot, which is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import socket, multiprocessing, time
import os
import re
from datetime import date
import sqlite3
import urllib.request
import imp
import html.parser

import db_process
import config
import spam_filter
import process_commands
### irc events in 'irc' directory
from irc import *
### notifications package
from notifications import *

# Defining a class to run the server. One per connection. This class will do most of our work.
class IRC_Server:

    # The default constructor - declaring our global variables
    def __init__(self, host, port, nick, channels, nickserv, nickserv_password, command_prefix, command_timeout, write_logs, log_channels, notifications_support, write_bug_notifications_to, write_commit_notifications_to, git_repos, change_topic_channel):
        self.irc_host = host
        self.irc_port = port
        self.irc_nick = nick
        self.channels = channels
        self.nickserv = nickserv
        self.nickserv_password = nickserv_password
        self.command_prefix = command_prefix
        self.command_timeout = command_timeout
        self.write_logs = write_logs
        self.log_channels = log_channels
        self.notifications_support = notifications_support
        self.write_bug_notifications_to = write_bug_notifications_to
        self.write_commit_notifications_to = write_commit_notifications_to
        self.git_repos = git_repos
        self.change_topic_channel = change_topic_channel
        self.irc_sock = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
        self.is_connected = False
        self.should_reconnect = False
        self.command = ""
        self.start_time = time.mktime(time.strptime( time.strftime('%Y-%m-%d-%H-%M-%S'), '%Y-%m-%d-%H-%M-%S'))

    ## The destructor - Close socket.
    def __del__(self):
        self.irc_sock.close()

    def ircbot(self):
        # Create database at first run
        if not os.path.exists('db/'+self.irc_host+'.sqlite'):
            db_process.start(self)

        conn, cur = self.db_data()
        sql = """UPDATE users
                SET state = 0;
                DELETE FROM user_channel;
        """
        cur.executescript(sql)
        conn.commit()
        cur.close()
        if ( self.notifications_support == True ):
            # run notifications
            print(("[%s] Notifications support...\t\tOK") % (self.irc_host))
            self.notifications()
        self.connect()

    def notifications(self):
        multiprocessing.Process(target=openra_topic.start, args=(self,)).start()
        multiprocessing.Process(target=openra_bugs.start, args=(self,)).start()
        multiprocessing.Process(target=github_commits.start, args=(self,)).start()
        multiprocessing.Process(target=openra_game.start, args=(self,)).start()

    # This is the bit that controls connection to a server & channel.
    def connect(self):
        self.should_reconnect = True
        try:
            self.irc_sock.connect ((self.irc_host, self.irc_port))
        except:
            print ("Error: Could not connect to IRC; Host: " + str(self.irc_host) + "Port: " + str(self.irc_port))
            exit(1) # We should make it recconect if it gets an error here
        print ("Connected to: " + str(self.irc_host) + ":" + str(self.irc_port))

        def bot_connect(self):
            str_buff = ("NICK %s \r\n") % (self.irc_nick)
            self.irc_sock.send (str_buff.encode())
            print (("[%s] Setting bot nick to " + str(self.irc_nick)) % (self.irc_host))

            str_buff = ("USER %s 8 * :X\r\n") % (self.irc_nick)
            self.irc_sock.send (str_buff.encode())
            print (("[%s] Setting User") % (self.irc_host))

            for channel in self.channels:
                str_buff = ( "JOIN %s \r\n" ) % (channel)
                self.irc_sock.send (str_buff.encode())
                print (("[%s] Joining channel " + channel) % (self.irc_host))
        bot_connect(self)
        
        if self.nickserv == True:
            print (("[%s] Sending request to identify with NickServ...") % (self.irc_host))
            data = "identify "+self.nickserv_password
            self.irc_sock.send( (("PRIVMSG %s :%s\r\n") % ('NickServ', data)).encode() )

        self.is_connected = True
        while True:
            if not self.listen():
                self.irc_nick = self.irc_nick + "_"
                bot_connect(self)

    def listen(self):
        while self.is_connected:
            recv = self.irc_sock.recv( 4096 )
            recv=self.decode_stream(recv)

            data = self.handle_recv(str(recv))
            for recv in data:
                if recv.find ( "PING" ) != -1:
                    self.irc_sock.send ( ("PONG "+ recv.split() [ 1 ] + "\r\n").encode() )

                if recv.find ( " PRIVMSG " ) != -1:
                    imp.reload(privmsg_e)
                    multiprocessing.Process(target=privmsg_e.parse_event, args=(self,recv,)).start()

                if recv.find ( " JOIN " ) != -1:
                    imp.reload(join_e)
                    join_e.parse_event(self, recv)

                if recv.find ( " QUIT " ) != -1:
                    imp.reload(quit_e)
                    quit_e.parse_event(self, recv)

                if recv.find ( " PART " ) != -1:
                    imp.reload(part_e)
                    part_e.parse_event(self, recv)

                if recv.find ( " NICK " ) != -1:
                    imp.reload(nick_e)
                    nick_e.parse_event(self, recv)

                if recv.find ( " TOPIC " ) != -1:
                    imp.reload(topic_e)
                    topic_e.parse_event(self, recv)

                if recv.find ( " KICK " ) != -1:
                    imp.reload(kick_e)
                    kick_e.parse_event(self, recv)

                if recv.find ( " MODE " ) != -1:
                    if ( recv.split()[0] != ":" + self.irc_nick ):
                        if recv.split()[3] in ['+v','-v','+o','-o','+h','-h']:
                            imp.reload(mode_e)
                            mode_e.parse_event(self, recv)

                if recv.find ( " 353 "+self.irc_nick ) != -1:     # NAMES
                    imp.reload(names_e)
                    names_e.parse_event(self, recv)

                if recv.find ( " NOTICE "+self.irc_nick+" :You are now identified for " ) != -1:
                    print(("[%s] NickServ Identification Succeeded\t\tOK") % (self.irc_host))

                if recv.find ( " 433 * "+self.irc_nick+" " ) != -1:
                    print(("[%s] Nick is already in use!!!") % (self.irc_host))
                    return False

        if self.should_reconnect:
            self.connect()

    def data_to_message(self, data):
        data = data[data.find(" :")+2:]
        return data

    #handle as single line request as multiple ( split recv into pieces before processing it )
    def handle_recv(self, recv):
        regex = re.compile('(.*?)\r\n')
        recv = regex.findall(recv)
        return recv

    # helper to remove some insanity.
    def send_reply(self, data, user, channel):
        target = channel if channel.startswith('#') else user
        self.send_message_to_channel(data,target)

    #another helper
    def decode_stream(self, stream):
        try:
            return stream.decode("utf8")
        except:
            return stream.decode("CP1252")

    # This function sends a message to a channel or user
    def send_message_to_channel(self, data, channel):
        print ( ( "[%s] %s: %s") % (self.irc_host, self.irc_nick, data) )
        self.irc_sock.send( (("PRIVMSG %s :%s\r\n") % (channel, data)).encode() )
        time.sleep(1)
        ### logs
        self.logs(self.irc_nick, channel, 'privmsg', str(data), '')

    def send_notice(self, data, user):
        print ( ( "[%s] NOTICE to %s: %s" ) % (self.irc_host, user, data) )
        str_buff = ( "NOTICE %s :%s\r\n" ) % (user,data)
        self.irc_sock.send (str_buff.encode())
        time.sleep(1)

    def send_names(self, channel):
        str_buff = ( "NAMES %s \r\n" ) % (channel)
        self.irc_sock.send (str_buff.encode())

    def get_names(self, channel):
        conn, cur = self.db_data()
        sql = """SELECT user FROM user_channel
                WHERE channel = '"""+channel+"""'
        """
        cur.execute(sql)
        records = cur.fetchall()
        conn.commit()
        cur.close()
        names = []
        for i in range(len(records)):
            names.append(records[i][0])
        return names

    def db_data(self):
        conn = sqlite3.connect('db/'+self.irc_host+'.sqlite')   # connect to database
        cur=conn.cursor()
        return (conn, cur)

    # This function takes a channel, which must start with a #.
    def join_channel(self, channel):
        if (channel[0] == "#"):
            str_buff = ( "JOIN %s \r\n" ) % (channel)
            self.irc_sock.send (str_buff.encode())
            # This needs to test if the channel is full

    # This function takes a channel, which must start with a #.
    def quit_channel(self, channel):
        if (channel[0] == "#"):
            str_buff = ( "PART %s \r\n" ) % (channel)
            self.irc_sock.send ( str_buff.encode() )
            # This needs to modify the list of active channels
    def topic(self, channel, topic):
        str_buff = ("TOPIC %s :%s\r\n") % (channel, topic)
        self.irc_sock.send ( str_buff.encode() )

        conn, cur = self.db_data()
        sql = """SELECT status FROM user_channel
                WHERE user = '"""+self.irc_nick+"""' AND channel = '"""+channel+"""'
        """
        cur.execute(sql)
        records = cur.fetchall()
        conn.commit()
        if ( len(records) != 0 ):   #at least, bot must be on a channel to send warning message
            if ( records[0][0] == '' or records[0][0] == None ):    #simple user
                self.send_message_to_channel( ("I've tried to change the topic of this channel but do not have rights for it"), channel)
        cur.close()

    def logs(self, irc_user, channel, logs_of, some_data, some_more_data):
        if self.write_logs == True:
            chan_d = str(channel).replace('#','')
            t = time.localtime( time.time() )
            time_prefix = time.strftime( '%Y-%m-%dT%T', t )
            log_dir = config.log_dir
            if ( log_dir[-1] != '/' ):
                log_dir = log_dir + '/'
            filename = log_dir + self.irc_host + '/' + chan_d + time.strftime( '/%Y/%m/%d', t )
            if channel in self.log_channels.split():
                if ( logs_of == 'privmsg' ):
                    row = ' <'+irc_user+'> '+some_data+'\n'
                elif ( logs_of == 'action' ):
                    row = ' * '+irc_user+' '+some_data+'\n'
                elif ( logs_of == 'join' ):
                    row = ' *** '+irc_user+' <'+some_data+'> has joined '+channel+'\n'
                elif ( logs_of == 'quit' ):
                    row = ' *** '+irc_user+' <'+some_data+'> has quit IRC'+some_more_data+'\n'
                elif ( logs_of == 'part' ):
                    row = ' *** '+irc_user+' <'+some_data+'> has left '+channel+'\n'
                elif ( logs_of == 'nick' ):
                    row = ' *** '+irc_user+' is now known as '+some_data+'\n'
                elif ( logs_of == 'topic' ):
                    row = ' *** '+irc_user+' changes topic to "'+some_data+'"\n'
                elif ( logs_of == 'kick' ):
                    row = ' *** '+irc_user+' was kicked by '+some_data+' ('+some_more_data+')\n'
                elif ( logs_of == 'mode' ):
                    row = ' *** ' + some_data
                else:
                    return  # probably an error.
                dir = os.path.dirname(filename)
                try:
                    if not os.path.exists(dir):
                        os.makedirs(dir)
                    file = open(filename,'a')
                    file.write(time_prefix + row)
                    file.close()
                except:
                    print('####### ERROR !!! ###### Probably no write permissions to logs directory!')

    def parse_html(self, string):
        h = html.parser.HTMLParser()
        string = h.unescape(string)
        return string.strip()

    def data_from_url(self, url, bytes):
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        data = opener.open(url).read(bytes)
        try:
            encoding = str(data).lower().split('charset=')[1].split('"')[0]
            data = data.decode(encoding)
        except: #no encoding found
            data = data.decode('utf-8')
        return data

    def title_from_url(self, url):
        # todo: security: can force the bot to output anything we like into
        #                 the channel.
        data = self.data_from_url(url, 8192)
        rx_title = re.compile(r'<title>(.*?)</title>', re.IGNORECASE)
        titles = rx_title.findall(data.replace('\n',' '))
        if ( titles != [] ):
            title = self.parse_html(titles[0])
            return title
        else:
            raise Exception("Exception: " + url + " does not contain title")

    def parse_link(self, channel, user, message):
        if re.search('.*http.*://.*', message):
            
            def check_localnetwork(self, url):
                if re.search('127.*', url):
                    return True
                if re.search('192.168.*', url):
                    return True
                if url == 'localhost':
                    return True
                if re.search('10\..*', url):
                    return True
                return False
            
            matches = re.findall(r"http.?://[^\s]*", message)
            for http_link in matches:
                link = http_link.split('://')[1]
                if check_localnetwork(self, link):
                    return
                pre = http_link.split('http')[1].split('//')[0]
                link = 'http'+pre+'//'+link
                if re.search("^#", channel):
                    if re.search('http.*youtube.com/watch.*', link):
                        link = link.split('&')[0]
                        try:
                            title = self.title_from_url(link).split('- YouTube')[0]
                            if ( title != 'YouTube - Broadcast Yourself.' ):    #video exists
                                self.send_message_to_channel( ("Youtube: " + title), channel )
                        except Exception as e:
                            print(e)    #probably socket error or http 404 error in title_from_url() or title not found
                    else:
                        try:
                            title = self.title_from_url(link)
                            self.send_message_to_channel( ("Title: " + title), channel )
                        except Exception as e:
                            print(e)    #probably socket error or http 404 error in title_from_url() or title not found

    def parse_bug_num(self, channel, message):
        matches = re.findall("#([0-9]*)", message)
        if ( matches != [] ):
            if re.search("^#", channel):
                for bug_report in matches:
                    if ( bug_report == '' ):
                        return
                    url = 'http://bugs.open-ra.org/issues/'+bug_report
                    try:
                        fetched = self.title_from_url(url).split('OpenRA - ')[1].split(' - open-ra')[0]
                        self.send_message_to_channel( (fetched+" | "+url), channel )
                    except Exception as e:
                        print(e)

    # This function is for pickup matches code
    def players_for_mode(self, mode):
        return sum( map( int, mode.split('v') ) )

    # Special admin commands for Op/HalfOp/Voice
    def Admin(self, user, channel):
        conn, cur = self.db_data()
        sql = """SELECT status FROM user_channel
                WHERE user = '"""+user+"""' AND channel = '"""+channel+"""'
        """
        cur.execute(sql)
        records = cur.fetchall()
        conn.commit()
        if ( records[0][0] == '' or records[0][0] == None ):
            self.send_reply( ("No rights!"), user, channel )
            return False
        return True

    def process_command(self, user, channel):
        command = (self.command)
        # Break the command into pieces, so we can interpret it with arguments
        command = command.split()

############    COMMADS:
        ### All public commands go here
        # The command isn't case sensitive
        if spam_filter.start(self, user, channel):
            # This line makes sure an actual command was sent, not a plain command prefix
            if ( len(command) == 0):
                error = "Usage: "+self.command_prefix+"command [arguments]"
                self.send_reply( (error), user, channel )
                return
            imp.reload(process_commands)
            process_commands.evalCommand(self, command[0].lower(), user, channel)
#####
class BotCrashed(Exception): # Raised if the bot has crashed.
    pass

def main():
    # Here begins the main programs flow:
    for irc_server in config.servers:
        server_data = eval('config.'+irc_server)
        ircserver = IRC_Server(server_data['host'], server_data['port'], server_data['bot_nick'], server_data['channels'].split(), server_data['nickserv'], server_data['nickserv_password'], server_data['command_prefix'], server_data['command_timeout'], server_data['write_logs'], server_data['log_channels'], server_data['notifications'], server_data['write_bug_notifications_to'], server_data['write_commit_notifications_to'], server_data['git_repos'], server_data['change_topic_channel'])
        ircserver_process = multiprocessing.Process(None,ircserver.ircbot,name="IRC Server" )
        ircserver_process.start()
