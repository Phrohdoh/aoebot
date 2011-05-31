#!/usr/bin/python3
# -*- coding: utf-8 -*-
# This code was written for Python 3.1.1
# version 0.101

# Changelog:
# version 0.100
# Basic framework
#
# version 0.101
# Fixed an error if an admin used a command with an argument, that wasn't an admin-only command

import socket, sys, multiprocessing, time
import os
import re
from datetime import date
import sqlite3
import hashlib

# Hardcoding the root admin - it seems the best way for now
root_admin = "ihptru"
root_admin_password = "" #only for the successful first run, dont forget to remove it later

languages=['af','sq','ar','be','bg','ca','zh-CN','hr','cs','da','nl','en','et','tl','fi','fr','gl','de','el','iw','hi','hu','is','id','ga','it','ja','ko','lv','lt','mk','ml','mt','no','fa','pl','ro','ru','sr','sk','sl','es','sw','sv','th','tr','uk','vi','cy','yi']
real_langs=['Afrikaans','Albanian','Arabic','Belarusian','Bulgarian','Catalan','Chinese_Simplified','Croatian','Czech','Danish','Dutch','English','Estonian','Filipino','Finnish','French','Galician','German','Greek','Hebrew','Hindi','Hungarian','Icelandic','Indonesian','Irish','Italian','Japanese','Korean','Latvian','Lithuanian','Macedonian','Malay','Maltese','Norwegian','Persian','Polish','Romanian','Russian','Serbian','Slovak','Slovenian','Spanish','Swahili','Swedish','Thai','Turkish','Ukrainian','Vietnamese','Welsh','Yiddish']
codes=['AF','AX','AL','DZ','AS','AD','AO','AI','AQ','AG','AR','AM','AW','AU','AT','AZ','BS','BH','BD','BB','BY','BE','BZ','BJ','BM','BT','BO','BQ','BA','BW','BV','BR','IO','BN','BG','BF','BI','KH','CM','CA','CV','KY','CF','TD','CL','CN','CX','CC','CO','KM','CG','CD','CK','CR','CI','HR','CU','CW','CY','CZ','DK','DJ','DM','DO','EC','EG','SV','GQ','ER','EE','ET','FK','FO','FJ','FI','FR','GF','PF','TF','GA','GM','GE','DE','GH','GI','GR','GL','GD','GP','GU','GT','GG','GN','GW','GY','HT','HM','VA','HN','HK','HU','IS','IN','ID','IR','IQ','IE','IM','IL','IT','JM','JP','JE','JO','KZ','KE','KI','KP','KR','KW','KG','LA','LV','LB','LS','LR','LY','LI','LT','LU','MO','MK','MG','MW','MY','MV','ML','MT','MH','MQ','MR','MU','YT','MX','FM','MD','MC','MN','ME','MS','MA','MZ','MM','NA','NR','NP','NL','NC','NZ','NI','NE','NG','NU','NF','MP','NO','OM','PK','PW','PS','PA','PG','PY','PE','PH','PN','PL','PT','PR','QA','RE','RO','RU','RW','BL','SH','KN','LC','MF','PM','VC','WS','SM','ST','SA','SN','RS','SC','SL','SG','SX','SK','SI','SB','SO','ZA','GS','ES','LK','SD','SR','SJ','SZ','SE','CH','SY','TW','TJ','TZ','TH','TL','TG','TK','TO','TT','TN','TR','TM','TC','TV','UG','UA','AE','GB','US','UM','UY','UZ','VU','VE','VN','VG','VI','WF','EH','YE','ZM','ZW']
match_codes=['AFGHANISTAN','ALAND ISLANDS','ALBANIA','ALGERIA','AMERICAN SAMOA','ANDORRA','ANGOLA','ANGUILLA','ANTARCTICA','ANTIGUA and BARBUDA','ARGENTINA','ARMENIA','ARUBA','AUSTRALIA','AUSTRIA','AZERBAIJAN','BAHAMAS','BAHRAIN','BANGLADESH','BARBADOS','BELARUS','BELGIUM','BELIZE','BENIN','BERMUDA','BHUTAN','BOLIVIA, PLURINATIONAL STATE OF','BONAIRE, SAINT EUSTATIUS and SABA','BOSNIA and HERZEGOVINA','BOTSWANA','BOUVET ISLAND','BRAZIL','BRITISH INDIAN OCEAN TERRITORY','BRUNEI DARUSSALAM','BULGARIA','BURKINA FASO','BURUNDI','CAMBODIA','CAMEROON','CANADA','CAPE VERDE','CAYMAN ISLANDS','CENTRAL AFRICAN REPUBLIC','CHAD','CHILE','CHINA','CHRISTMAS ISLAND','COCOS (KEELING) ISLANDS','COLOMBIA','COMOROS','CONGO','CONGO, THE DEMOCRATIC REPUBLIC OF THE','COOK ISLANDS','COSTA RICA',"COTE D'IVOIRE",'CROATIA','CUBA','CURACAO','CYPRUS','CZECH REPUBLIC','DENMARK','DJIBOUTI','DOMINICA','DOMINICAN REPUBLIC','ECUADOR','EGYPT','EL SALVADOR','EQUATORIAL GUINEA','ERITREA','ESTONIA','ETHIOPIA','FALKLAND ISLANDS (MALVINAS)','FAROE ISLANDS','FIJI','FINLAND','FRANCE','FRENCH GUIANA','FRENCH POLYNESIA','FRENCH SOUTHERN TERRITORIES','GABON','GAMBIA','GEORGIA','GERMANY','GHANA','GIBRALTAR','GREECE','GREENLAND','GRENADA','GUADELOUPE','GUAM','GUATEMALA','GUERNSEY','GUINEA','GUINEA-BISSAU','GUYANA','HAITI','HEARD ISLAND AND MCDONALD ISLANDS','HOLY SEE (VATICAN CITY STATE)','HONDURAS','HONG KONG','HUNGARY','ICELAND','INDIA','INDONESIA','IRAN, ISLAMIC REPUBLIC OF','IRAQ','IRELAND','ISLE OF MAN','ISRAEL','ITALY','JAMAICA','JAPAN','JERSEY','JORDAN','KAZAKHSTAN','KENYA','KIRIBATI',"KOREA, DEMOCRATIC PEOPLE'S REPUBLIC OF",'KOREA, REPUBLIC OF','KUWAIT','KYRGYZSTAN',"LAO PEOPLE'S DEMOCRATIC REPUBLIC",'LATVIA','LEBANON','LESOTHO','LIBERIA','LIBYAN ARAB JAMAHIRIYA','LIECHTENSTEIN','LITHUANIA','LUXEMBOURG','MACAO','MACEDONIA, THE FORMER YUGOSLAV REPUBLIC OF','MADAGASCAR','MALAWI','MALAYSIA','MALDIVES','MALI','MALTA','MARSHALL ISLANDS','MARTINIQUE','MAURITANIA','MAURITIUS','MAYOTTE','MEXICO','MICRONESIA, FEDERATED STATES OF','MOLDOVA, REPUBLIC OF','MONACO','MONGOLIA','MONTENEGRO','MONTSERRAT','MOROCCO','MOZAMBIQUE','MYANMAR','NAMIBIA','NAURU','NEPAL','NETHERLANDS','NEW CALEDONIA','NEW ZEALAND','NICARAGUA','NIGER','NIGERIA','NIUE','NORFOLK ISLAND','NORTHERN MARIANA ISLANDS','NORWAY','OMAN','PAKISTAN','PALAU','PALESTINIAN TERRITORY, OCCUPIED','PANAMA','PAPUA NEW GUINEA','PARAGUAY','PERU','PHILIPPINES','PITCAIRN','POLAND','PORTUGAL','PUERTO RICO','QATAR','REUNION','ROMANIA','RUSSIAN FEDERATION','RWANDA','SAINT BARTHELEMY','SAINT HELENA, ASCENSION and TRISTAN DA CUNHA','SAINT KITTS and NEVIS','SAINT LUCIA','SAINT MARTIN (FRENCH PART)','SAINT PIERRE and MIQUELON','SAINT VINCENT and THE GRENADINES','SAMOA','SAN MARINO','SAO TOME and PRINCIPE','SAUDI ARABIA','SENEGAL','SERBIA','SEYCHELLES','SIERRA LEONE','SINGAPORE','SINT MAARTEN (DUTCH PART)','SLOVAKIA','SLOVENIA','SOLOMON ISLANDS','SOMALIA','SOUTH AFRICA','SOUTH GEORGIA and THE SOUTH SANDWICH ISLANDS','SPAIN','SRI LANKA','SUDAN','SURINAME','SVALBARD and JAN MAYEN','SWAZILAND','SWEDEN','SWITZERLAND','SYRIAN ARAB REPUBLIC','TAIWAN, PROVINCE OF CHINA','TAJIKISTAN','TANZANIA, UNITED REPUBLIC OF','THAILAND','TIMOR-LESTE','TOGO','TOKELAU','TONGA','TRINIDAD and TOBAGO','TUNISIA','TURKEY','TURKMENISTAN','TURKS and CAICOS ISLANDS','TUVALU','UGANDA','UKRAINE','UNITED ARAB EMIRATES','UNITED KINGDOM','UNITED STATES','NITED STATES MINOR OUTLYING ISLANDS','URUGUAY','UZBEKISTAN','VANUATU','VENEZUELA, BOLIVARIAN REPUBLIC OF','VIET NAM','VIRGIN ISLANDS, BRITISH','VIRGIN ISLANDS, U.S.','WALLIS and FUTUNA','WESTERN SAHARA','YEMEN','ZAMBIA','ZIMBABWE']

# Defining a class to run the server. One per connection. This class will do most of our work.
class IRC_Server:

    # The default constructor - declaring our global variables
    # channel should be rewritten to be a list, which then loops to connect, per channel.
    # This needs to support an alternate nick.
    def __init__(self, host, port, nick, channel , password =""):
        self.irc_host = host
        self.irc_port = port
        self.irc_nick = nick
        self.irc_channel = channel
        self.irc_sock = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
        self.is_connected = False
        self.should_reconnect = False
        self.command = ""

    ## The destructor - Close socket.
    def __del__(self):
        self.irc_sock.close()

    # This is the bit that controls connection to a server & channel.
    # It should be rewritten to allow multiple channels in a single server.
    # This needs to have an "auto identify" as part of its script, or support a custom connect message.
    def connect(self):
        self.should_reconnect = True
        try:
            self.irc_sock.connect ((self.irc_host, self.irc_port))
        except:
            print ("Error: Could not connect to IRC; Host: " + str(self.irc_host) + "Port: " + str(self.irc_port))
            exit(1) # We should make it recconect if it gets an error here
        print ("Connected to: " + str(self.irc_host) + ":" + str(self.irc_port))

        str_buff = ("NICK %s \r\n") % (self.irc_nick)
        self.irc_sock.send (str_buff.encode())
        print ("Setting bot nick to " + str(self.irc_nick) )

        str_buff = ("USER %s 8 * :X\r\n") % (self.irc_nick)
        self.irc_sock.send (str_buff.encode())
        print ("Setting User")
        # Insert Alternate nick code here.

        # Insert Auto-Identify code here.

        str_buff = ( "JOIN %s \r\n" ) % (self.irc_channel)
        self.irc_sock.send (str_buff.encode())
        print ("Joining channel " + str(self.irc_channel) )
        self.is_connected = True
        self.listen()
        
    def listen(self):
        while self.is_connected:
            recv = self.irc_sock.recv( 4096 )
            ###for logs
            a = date.today()
            a = str(a)
            a = a.split('-')
            year = a[0]
            month = a[1]
            day = a[2]
            b = time.localtime()
            b = str(b)
            hours = b.split('tm_hour=')[1].split(',')[0]
            minutes = b.split('tm_min=')[1].split(',')[0]
            if len(hours) == 1:
                real_hours = '0'+hours
            else:
                real_hours = hours
            if len(minutes) == 1:
                real_minutes = '0'+minutes
            else:
                real_minutes = minutes
            ###
            if str(recv).find ( "PING" ) != -1:
                self.irc_sock.send ( "PONG ".encode() + recv.split() [ 1 ] + "\r\n".encode() )
            #recover all nicks on channel
            #if str(recv).find ( "353 orabot =" ) != -1:
            #    print (str(recv))
            #    user_nicks = str(recv).split(':')[2].rstrip()
            #    user_nicks = user_nicks.replace('+','').replace('@','')
            #    user_nicks = user_nicks.split(' ')
            #    self.nicks = user_nicks
            if str(recv).find ( "PRIVMSG" ) != -1:
                irc_user_nick = str(recv).split ( '!' ) [ 0 ] . split ( ":")[1]
                irc_user_host = str(recv).split ( '@' ) [ 1 ] . split ( ' ' ) [ 0 ]
                irc_user_message = self.data_to_message(str(recv)).encode('utf-8').decode('utf-8')
                irc_user_message = str(irc_user_message)
                # if PRIVMSG is still in string - message from person with ipv6
                suit = re.compile('PRIVMSG')
                if suit.search(irc_user_message):
                    irc_user_message = str(recv).split ( 'PRIVMSG' ) [ 1 ] . split ( ' :') [ 1 ]
                    irc_user_message = irc_user_message[:-5].encode('utf-8').decode('utf-8')
                    irc_user_message = str(irc_user_message)
                ###logs
                chan = str(recv).split ( 'PRIVMSG' ) [ 1 ] . lstrip() . split(' :')[0]  #channel ex: #openra
                if chan == '#openra' or chan == '#openra-dev':
                    row = '['+real_hours+':'+real_minutes+'] '+irc_user_nick+': '+str(irc_user_message)+'\n'
                    if chan == '#openra':
                        chan_d = 'openra'
                    elif chan == '#openra-dev':
                        chan_d = 'openra-dev'
                    else:
                        chan_d = 'pms'
                    filename = '/var/openra/irc/logs/'+chan_d+'/'+year+'/'+month+'/'+day
                    dir = os.path.dirname(filename)
                    if not os.path.exists(dir):
                        os.makedirs(dir)
                    file = open(filename,'a')
                    file.write(row)
                    file.close()
                ###
                print ( irc_user_nick + ": " + irc_user_message)
                # "!" Indicated a command
                if ( str(irc_user_message[0]) == "]" ):
                    self.command = str(irc_user_message[1:])
                    # (str(recv)).split()[2] ) is simply the channel the command was heard on.
                    self.process_command(irc_user_nick, ( (str(recv)).split()[2] ))
            if str(recv).find ( "JOIN" ) != -1:
                print (str(recv))
                irc_join_nick = str(recv).split( '!' ) [ 0 ].split( ':' ) [ 1 ]
                irc_join_host = str(recv).split( '!' ) [ 1 ].split( ' ' ) [ 0 ]
                chan = str(recv).split( "JOIN" ) [ 1 ].lstrip().split( ":" )[1].rstrip()     #channle ex: #openra
                
                #uncomment below on the first run
                #conn = sqlite3.connect('../db/users.db')
                #cur=conn.cursor()
                #sql = """CREATE TABLE users (
                #uid integer NOT NULL,
                #user varchar(30) NOT NULL
                #)               
                #"""
                #cur.execute(sql)
                #conn.commit()
                #sql= """INSERT INTO users
                #        (uid,user)
                #        VALUES
                #        (
                #        1,'test'
                #        )
                #"""
                #cur.execute(sql)
                #conn.commit()
                #cur.close()
                #conn = sqlite3.connect('../db/later.db')
                #cur=conn.cursor()
                #sql = """CREATE TABLE later (
                #        uid integer NOT NULL,
                #        sender varchar(30) NOT NULL,
                #        reciever varchar(30) NOT NULL,
                #        channel varchar(30) NOT NULL,
                #        date date NOT NULL,
                #        message varchar(1000) NOT NULL
                #)             
                #"""
                #cur.execute(sql)
                #conn.commit()
                #sql = """INSERT INTO later
                #        (uid,sender,reciever,channel,date,message)
                #        VALUES
                #        (
                #        1,'test','test','#test',strftime('%Y-%m-%d-%H-%M-%S'),'Hello, how are you?'
                #        )                
                #"""
                #cur.execute(sql)
                #conn.commit()
                #cur.close()
                
                conn = sqlite3.connect('../db/users.db')
                cur=conn.cursor()
                sql = """SELECT * FROM users
                        WHERE user = '"""+irc_join_nick+"'"+"""
                """
                cur.execute(sql)
                conn.commit()
                row = []
                for row in cur:
                    pass
                cur.close()
                if irc_join_nick not in row:     #user NOT found, add him (if user is not in db, he could not have ]later message)
                    #get last uid
                    conn = sqlite3.connect('../db/users.db')
                    cur=conn.cursor()
                    sql = """SELECT * FROM users
                            ORDER BY uid DESC LIMIT 1
                    """
                    cur.execute(sql)
                    conn.commit()
                    row = []
                    for row in cur:
                        pass
                    cur.close()
                    uid_users = row[0]
                    uid_users = uid_users + 1   # uid + 1
                    conn = sqlite3.connect('../db/users.db')
                    cur=conn.cursor()
                    sql = """INSERT INTO users
                            (uid,user)
                            VALUES
                            (
                            """+str(uid_users)+",'"+str(irc_join_nick)+"'"+"""
                            )
                    """
                    cur.execute(sql)
                    conn.commit()
                    cur.close()
                else:   #he can have ]later messages
                    conn = sqlite3.connect('../db/later.db')
                    cur=conn.cursor()
                    sql = """SELECT reciever FROM later
                            WHERE reciever = '"""+irc_join_nick+"'"+"""
                    """
                    cur.execute(sql)
                    conn.commit()

                    row = []
                    for row in cur:
                        pass
                    cur.close()
                    if irc_join_nick in row:    #he has messages in database, read it
                        conn = sqlite3.connect('../db/later.db')
                        cur=conn.cursor()
                        sql = """SELECT * FROM later
                                WHERE reciever = '"""+irc_join_nick+"'"+"""
                        """
                        cur.execute(sql)
                        conn.commit()
                        row = []
                        msgs = []
                        for row in cur:
                            msgs.append(row)
                        cur.close()
                        msgs_length = len(msgs) #number of messages for player
                        self.send_message_to_channel( ("You have "+str(msgs_length)+" offline messages:"), irc_join_nick )
                        for i in range(int(msgs_length)):
                            who_sent = msgs[i][1]
                            on_channel = msgs[i][3]
                            message_date = msgs[i][4]
                            offline_message = msgs[i][5]
                            self.send_message_to_channel( ("### From: "+who_sent+";  channel: "+on_channel+";  date: "+message_date), irc_join_nick )
                            self.send_message_to_channel( (offline_message), irc_join_nick )
                        time.sleep(0.1)
                        conn = sqlite3.connect('../db/later.db')
                        cur=conn.cursor()
                        sql = """DELETE FROM later
                                WHERE reciever = '"""+irc_join_nick+"'"+"""
                        
                        """
                        
                        cur.execute(sql)
                        conn.commit()
                        cur.close() 
                ###logs
                if chan == '#openra' or chan == '#openra-dev':
                    row = '['+real_hours+':'+real_minutes+'] '+'* '+irc_join_nick+' ('+irc_join_host+') has joined '+chan+'\n'
                    if chan == '#openra':
                        chan_d = 'openra'
                    elif chan == '#openra-dev':
                        chan_d = 'openra-dev'
                    else:
                        chan_d = 'pms'
                    filename = '/var/openra/irc/logs/'+chan_d+'/'+year+'/'+month+'/'+day
                    dir = os.path.dirname(filename)
                    if not os.path.exists(dir):
                        os.makedirs(dir)
                    file = open(filename,'a')
                    file.write(row)
                    file.close()
                ###
            if str(recv).find ( "PART" ) != -1:
                print (str(recv))
                irc_part_nick = str(recv).split( "!" )[ 0 ].split( ":" ) [ 1 ]
                ###logout
                conn = sqlite3.connect('../db/register.db')
                cur = conn.cursor()
                sql = """SELECT * FROM register
                        WHERE user = '"""+irc_part_nick+"'"+"""
                """
                cur.execute(sql)
                conn.commit()
                row = []
                for row in cur:
                    pass
                cur.close()
                if irc_part_nick in row:
                    authenticated = row[4]
                    if authenticated == 1:
                        conn = sqlite3.connect('../db/register.db')
                        cur = conn.cursor()
                        sql = """UPDATE register
                                SET authenticated = 0
                                WHERE user = '"""+irc_part_nick+"'"+"""
                        """
                        cur.execute(sql)
                        conn.commit()
                        cur.close()              
                
                ###logs
                chan = str(recv).split( "PART" ) [ 1 ].split( " #" ) [ 1 ].split( " " ) [ 0 ]
                chan = '#'+chan     #channel ex: #openra
                if chan == '#openra' or chan == '#openra-dev':
                    row = '['+real_hours+':'+real_minutes+'] '+'* '+irc_part_nick+' has quit\n'
                    if chan == '#openra':
                        chan_d = 'openra'
                    elif chan == '#openra-dev':
                        chan_d = 'openra-dev'
                    else:
                        chan_d = 'pms'
                    filename = '/var/openra/irc/logs/'+chan_d+'/'+year+'/'+month+'/'+day
                    dir = os.path.dirname(filename)
                    if not os.path.exists(dir):
                        os.makedirs(dir)
                    file = open(filename,'a')
                    file.write(row)
                    file.close()
                ###
                
        if self.should_reconnect:
            self.connect()

    def data_to_message(self,data):
        data = data[data.find(':')+1:len(data)]
        data = data[data.find(':')+1:len(data)]
        data = str(data[0:len(data)-5])
        return data

    # This function sends a message to a channel, which must start with a #.
    def send_message_to_channel(self,data,channel):
        print ( ( "%s: %s") % (self.irc_nick, data) )
        self.irc_sock.send( (("PRIVMSG %s :%s\r\n") % (channel, data)).encode() )

    # This function takes a channel, which must start with a #.
    def join_channel(self,channel):
        if (channel[0] == "#"):
            str_buff = ( "JOIN %s \r\n" ) % (channel)
            self.irc_sock.send (str_buff.encode())
            # This needs to test if the channel is full
            # This needs to modify the list of active channels

    # This function takes a channel, which must start with a #.
    def quit_channel(self,channel):
        if (channel[0] == "#"):
            str_buff = ( "PART %s \r\n" ) % (channel)
            self.irc_sock.send (str_buff.encode())
            # This needs to modify the list of active channels


    # This nice function here runs ALL the commands.
    # For now, we only have 2: root admin, and anyone.
    def process_command(self, user, channel):
        # This line makes sure an actual command was sent, not a plain "!"
        if ( len(self.command.split()) == 0):
            error = "Usage: ]command [arguments]"
            if re.search("^#", channel):
                self.send_message_to_channel( (error), channel)
            else:
                self.send_message_to_channel( (error), user)
            return
        # So the command isn't case sensitive
        command = (self.command).lower()
        # Break the command into pieces, so we can interpret it with arguments
        command = command.split()
        string_command = " ".join(command)
        
        #uncomment strings below at first script run
        #conn = sqlite3.connect('../db/register.db')
        #cur = conn.cursor()
        #sql = """CREATE TABLE register (
        #uid int NOT NULL,
        #user varchar(20) NOT NULL,
        #pass varchar(50),
        #owner boolean NOT NULL DEFAULT '0',
        #authenticated boolean NOT NULL DEFAULT '0'
        #)
        #"""
        #cur.execute(sql)
        #conn.commit()
        #
        #user_password = hashlib.md5(root_admin_password.encode('utf-8')).hexdigest()     
        #sql = """INSERT INTO register
        #        (uid,user,pass,owner)
        #        VALUES
        #        (
        #        1,'"""+root_admin+"','"+str(user_password)+"'"+""",1
        #        )       
        #"""
        #cur.execute(sql)
        #conn.commit()
        #cur.close()
        #conn = sqlite3.connect('../db/black_list.db')
        #cur=conn.cursor()
        #sql = """CREATE TABLE black_list (
        #    uid integer NOT NULL,
        #    user varchar(30) NOT NULL,
        #    date_time date NOT NULL,
        #    count integer NOT NULL
        #    )        
        #"""
        #cur.execute(sql)
        #conn.commit()
        #sql = """INSERT INTO black_list
        #       (uid,user,date_time,count)
        #       VALUES
        #       (
        #       1,'test',strftime('%Y-%m-%d-%H-%M'),1
        #       )
        #"""
        #cur.execute(sql)
        #conn.commit()
        #cur.close()
        # 
        #conn = sqlite3.connect('../db/commands.db')
        #cur=conn.cursor()
        #sql = """CREATE TABLE commands (
        #        uid integer NOT NULL,
        #        user varchar(30) NOT NULL,
        #        command varchar(300) NOT NULL,
        #        date_time date NOT NULL
        #)
        #"""
        #cur.execute(sql)
        #conn.commit()
        #for i in range(31):
        #    sql = """INSERT INTO commands
        #        (uid,user,command,date_time)
        #        VALUES
        #        (
        #        1,'test','test_command',strftime('%Y-%m-%d-%H-%M-%S')
        #        )
        #    """
        #    cur.execute(sql)
        #    conn.commit()
        #    cur.close()     

        conn = sqlite3.connect('../db/black_list.db')
        cur=conn.cursor()
        sql = """SELECT * FROM black_list
            WHERE user = '"""+user+"'"+"""
        """
        cur.execute(sql)
        conn.commit()
        
        row = []
        for row in cur:
            pass
        cur.close()
        check_ignore = '0'
        if user in row:
            ignore_count = row[3]
            ignore_minutes = str(ignore_count)+'0'
            ignore_date = "".join(str(row[2]).split('-'))
            a = date.today()
            a = str(a)
            a = a.split('-')
            year = a[0]
            month = a[1]
            day = a[2]
            b = time.localtime()
            b = str(b)
            hours = b.split('tm_hour=')[1].split(',')[0]
            minutes = b.split('tm_min=')[1].split(',')[0]
            if len(hours) == 1:
                hours = '0'+hours
            else:
                hours = hours
            if len(minutes) == 1:
                minutes = '0'+minutes
            else:
                minutes = minutes
            localtime = year+month+day+hours+minutes
            difference = int(localtime) - int(ignore_date)  #how many minutes after last ignore
            if int(difference) < int(ignore_minutes):
                check_ignore = '1'  #lock, start ignore
            else:   #no need to ignore, ignore_minutes < difference
                check_ignore = '0'
        if check_ignore == '0':
            #get last uid_commands
            conn = sqlite3.connect('../db/commands.db')
            cur=conn.cursor()
            sql = """SELECT * FROM commands
                    ORDER BY uid DESC LIMIT 1
            """
            cur.execute(sql)
            conn.commit()
            
            for row in cur:
                pass
            cur.close()
            uid_commands=row[0]
            
            uid_commands = uid_commands + 1
            #clear 'commands' table after each 1 000 000 record
            if uid_commands >= 1000000:
                uid_commands = 1
                conn = sqlite3.connect('../db/commands.db')
                cur=conn.cursor()
                sql = """DELETE FROM commands"""
                cur.execute(sql)
                conn.commit()
                cur.close()
    
            #write each command into 'commands' table
            conn = sqlite3.connect('../db/commands.db')
            cur=conn.cursor()   
            sql = """INSERT INTO commands
                    (uid,user,command,date_time)
                    VALUES
                    (
                    """+str(uid_commands)+",'"+user+"','"+string_command+"',"+"strftime('%Y-%m-%d-%H-%M-%S')"+""" 
                    )        
            """
            cur.execute(sql)
            conn.commit()
            cur.close()
            
            #extract last 30 records
            conn = sqlite3.connect('../db/commands.db')
            cur=conn.cursor()
            sql = """SELECT * FROM commands
                ORDER BY uid DESC LIMIT 30
            """
            cur.execute(sql)
            conn.commit()
            
        
            var=[]
            for row in cur:
                var.append(row)
            var.reverse()
            cur.close()
            actual=[]
            user_data=[]
            for i in range(30):
                if user in str(var[i][1]):
                    actual.append(str(var[i][1]))   #name
                    actual.append(str(var[i][3]))   #date and time
                    user_data.append(actual)
                    actual=[]
            user_data_length = len(user_data)
            if user_data_length > 10:
                #get player's (last - 10) record
                user_data_len10 = user_data_length - 10
                actual=user_data[user_data_len10]
                first_date="".join(actual[1].split('-'))    #last - 10 record
                last_date="".join(user_data[user_data_length-1][1].split('-'))  #current date/time
                seconds_range=int(last_date)-int(first_date)  #how many seconds between player's commands
                if seconds_range < 30:  #player made more then 10 commands in range of 30 seconds. It is too quick, spam!
                    conn = sqlite3.connect('../db/black_list.db')
                    cur=conn.cursor()
                    sql = """SELECT * FROM black_list
                            WHERE user = '"""+user+"'"+"""
                    """
                    cur.execute(sql)
                    conn.commit()

                    row = []
                    for row in cur:
                        pass
                    cur.close()
                    if user not in row:   #user does not exist in 'black_list' table yet
                        #get last uid_black_list
                        conn = sqlite3.connect('../db/black_list.db')
                        cur=conn.cursor()
                        sql = """SELECT * FROM black_list
                                ORDER BY uid DESC LIMIT 1
                        """
                        cur.execute(sql)
                        conn.commit()
       
                        for row in cur:
                            pass
                        cur.close()
                        uid_black_list=row[0]
                        uid_black_list = uid_black_list + 1
                        
                        conn = sqlite3.connect('../db/black_list.db')
                        cur=conn.cursor()
                        sql = """INSERT INTO black_list
                            (uid,user,date_time,count)
                            VALUES
                            (
                            """+str(uid_black_list)+",'"+user+"',strftime('%Y-%m-%d-%H-%M'),"+str(1)+"""
                            )                   
                        """
                        cur.execute(sql)
                        conn.commit()
                        cur.close()
                    else:   #in row : exists in 'black_table'
                        count_ignore = row[3]
                        count_ignore = count_ignore + 1
                        conn = sqlite3.connect('../db/black_list.db')
                        cur=conn.cursor()
                        sql = """UPDATE black_list
                                SET count = """+str(count_ignore)+", "+"""date_time = strftime('%Y-%m-%d-%H-%M')
                                WHERE user = '"""+user+"'"+""" 
                        """
                        cur.execute(sql)
                        conn.commit()
                        cur.close()
                    conn = sqlite3.connect('../db/black_list.db')
                    cur=conn.cursor()
                    sql = """SELECT * FROM black_list
                        WHERE user = '"""+user+"'"+"""
                    """
                    cur.execute(sql)
                    conn.commit()

                    row = []
                    for row in cur:
                        pass
                    cur.close()
                    if user in row:
                        ignore_count = row[3]
                        ignore_minutes = str(ignore_count)+'0'
                        check_ignore = '1'  #lock, start ignore        
                        if re.search("^#", channel):
                            self.send_message_to_channel( (user+", your actions are counted as spam, I will ignore you for "+str(ignore_minutes)+" minutes"), channel )
                        else:
                            self.send_message_to_channel( (user+", your actions are counted as spam, I will ignore you for "+str(ignore_minutes)+" minutes"), user )        
                        return
############    commands
            conn = sqlite3.connect('../db/register.db')
            cur = conn.cursor()
            sql = """SELECT * FROM register
                    WHERE user = '"""+user+"'"+"""
            """
            cur.execute(sql)
            conn.commit()
            row = []
            for row in cur:
                pass
            cur.close()
            if user in row:     #user exists in 'register' table
                owner = row[3]
                authenticated = row[4]
                if (authenticated == 1):    #he is also authenticated           
                    # All admin only commands go in here.
                    # The first set of commands are ones that don't take parameters
                    if ( len(command) == 1):
    
                        #This command shuts the bot down.
                        if (command[0] == "quit"):
                            str_buff = ( "QUIT %s \r\n" ) % (channel)
                            self.irc_sock.send (str_buff.encode())
                            self.irc_sock.close()
                            self.is_connected = False
                            self.should_reconnect = False
                        if (command[0] == "log"):
                            if not re.search("^#", channel):
                                conn = sqlite3.connect('../db/commands.db')
                                cur = conn.cursor()
                                sql = """SELECT * FROM commands
                                        ORDER BY uid DESC LIMIT 10
                                """
                                cur.execute(sql)
                                conn.commit()
                                row = []
                                logs = []
                                actual = []
                                for row in cur:
                                    logs.append(row)
                                cur.close()
                                for i in range(int(len(logs))):
                                    actual.append(logs[i][1])
                                    actual.append(logs[i][2])
                                    actual.append(logs[i][3])
                                    self.send_message_to_channel( ("User: "+actual[0]+"; Date: "+actual[2]+"; Command: ]"+actual[1]), user)
                                    actual = []
                                    time.sleep(0.5)
                    # These commands take parameters
                    else:
                        if (len(command) == 2):
                            if (command[0] == "add"):
                                nick = command[1]
                                conn = sqlite3.connect('../db/users.db')
                                cur=conn.cursor()
                                sql = """SELECT * FROM users
                                        ORDER BY uid DESC LIMIT 1
                                """
                                cur.execute(sql)
                                conn.commit()
                                for row in cur:
                                    pass
                                cur.close()
                                uid_users=row[0]
                                uid_users = uid_users + 1
                            
                                conn = sqlite3.connect('../db/users.db')
                                cur = conn.cursor()
                                sql = """SELECT * FROM users
                                        WHERE user = '"""+nick+"'"+"""
                                """
                                cur.execute(sql)
                                conn.commit()
                                row = []
                                for row in cur:
                                    pass
                                cur.close()
                                if nick in row: #users exists in database already
                                    if re.search("^#", channel):
                                        self.send_message_to_channel( ("Error! User already exists"), channel)
                                    else:
                                        self.send_message_to_channel( ("Error! User already exists"), user)
                                else:   
                                    conn = sqlite3.connect('../db/users.db')
                                    cur=conn.cursor()
                                    sql = """INSERT INTO users
                                        (uid,user)
                                        VALUES
                                        (
                                        """+str(uid_users)+",'"+nick+"'"+"""
                                        )
                                    """
                                    cur.execute(sql)
                                    conn.commit()
                                    cur.close()
                                    if re.search("^#", channel):
                                        self.send_message_to_channel( ("Confirmed"), channel)
                                    else:
                                        self.send_message_to_channel( ("Confirmed"), user)
                            # This command makes the bot join a channel
                            # This needs to be rewritten in a better way, to catch multiple channels
                            if (command[0] == "join"):
                                if ( (command[1])[0] == "#"):
                                    irc_channel = command[1]
                                else:
                                    irc_channel = "#" + command[1]
                                self.join_channel(irc_channel)
    
                            # This command makes the bot part a channel
                            # This needs to be rewritten in a better way, to catch multiple channels
                            if (command[0] == "part"):
                                if ( (command[1])[0] == "#"):
                                    irc_channel = command[1]
                                else:
                                    irc_channel = "#" + command[1]
                                self.quit_channel(irc_channel)
                    if (owner == 1):    #owner commands go here
                        if not re.search("^#", channel):    #owner commands only in private
                            if (len(command) == 2):
                                if (command[0] == "register"):      #owner command to allow users register
                                    register_nick = command[1]
                                    conn = sqlite3.connect('../db/register.db')
                                    cur = conn.cursor()
                                    sql = """SELECT * FROM register
                                            WHERE user = '"""+register_nick+"'"+"""
                                    """
                                    cur.execute(sql)
                                    conn.commit()
                                    row = []
                                    for row in cur:
                                        pass
                                    cur.close()
                                    if register_nick in row:
                                        self.send_message_to_channel( ("User "+register_nick+" already exists"), user)
                                    else:
                                        conn = sqlite3.connect('../db/register.db')
                                        cur = conn.cursor()
                                        sql = """SELECT * FROM register
                                                ORDER BY uid DESC LIMIT 1                                       
                                        """
                                        cur.execute(sql)
                                        conn.commit()
                                        row = []
                                        for row in cur:
                                            pass
                                        uid_register = row[0]
                                        uid_register = uid_register + 1
                                        sql = """INSERT INTO register
                                                (uid,user)
                                                VALUES
                                                (
                                                """+str(uid_register)+",'"+register_nick+"'"+"""
                                                )
                                        """
                                        cur.execute(sql)
                                        conn.commit()
                                        cur.close()
                                        self.send_message_to_channel( ("User "+register_nick+" added successfully, he can use ]register to set up a password"), user)
                                    
    
            # All public commands go here
            #########################################################################################
            if ( len(command) > 3):
                if ( command[0] == "tr"):
                    if command[1] in languages:
                        if command[2] in languages:
                            filename = 'tr.temp'
                            length = len(command)
                            line=''
                            for i in range(length):
                                line = line+command[i]+' '
                            line = line.lstrip().rstrip()
                            file = open(filename, 'w')
                            file.write(line)
                            file.close()
                            os.system("python ../tr.py")
                            time.sleep(0.5)
                            filename = 'tr.text'
                            file = open(filename, 'r')
                            text = file.readline()
                            file.close()
                            if re.search("^#", channel):
                                self.send_message_to_channel( (text), channel)
                            else:
                                self.send_message_to_channel( (text), user)
            if ( len(command) > 2):
                if ( command[0] == "later" ):
                    if re.search("^#", channel):
                        user_nick = command[1] #reciever
                        if user_nick == user:
                            self.send_message_to_channel( (user+", you can not send a message to yourself"), channel)
                        else:
                            user_message = " ".join(command[2:])  #message
                            #send NAMES channel to server
                            str_buff = ( "NAMES %s \r\n" ) % (channel)
                            self.irc_sock.send (str_buff.encode())
                            #recover all nicks on channel
                            recv = self.irc_sock.recv( 4096 )
                        
                            if str(recv).find ( "353 orabot =" ) != -1:
                                print (str(recv))
                                user_nicks = str(recv).split(':')[2].rstrip()
                                user_nicks = user_nicks.replace('+','').replace('@','')
                                user_nicks = user_nicks.split(' ')
                            
                            if user_nick in user_nicks:  #reciever is on the channel right now
                                self.send_message_to_channel( (user+", "+user_nick+" is on the channel right now! Write to him using /msg or /query"), channel)
                            else:   #reciever is not on the channel
                                #check if he exists in database
                                conn = sqlite3.connect('../db/users.db')
                                cur=conn.cursor()
                                sql = """SELECT user FROM users
                                        WHERE user = '"""+user_nick+"'"+"""
                                
                                """
                                cur.execute(sql)
                                conn.commit()
                                cur.close()
                                row = ''
                                for row in cur:
                                    pass
                                if user_nick not in row:
                                    self.send_message_to_channel( ("Error! No such user in my database"), channel)
                                else:   #users exists
                                    #get uid
                                    conn = sqlite3.connect('../db/later.db')
                                    cur=conn.cursor()
                                    sql = """SELECT * FROM later
                                            ORDER BY uid DESC LIMIT 1
                                    """
                                    cur.execute(sql)
                                    conn.commit()
                                    cur.close()
                                    row = ''
                                    for row in cur:
                                        pass
                                    uid_later=row[0]
                                    uid_later = uid_later + 1
                                    conn = sqlite3.connect('../db/later.db')
                                    cur=conn.cursor()
                                    sql = """INSERT INTO later
                                            (uid,sender,reciever,channel,date,message)
                                            VALUES
                                            (
                                            """+str(uid_later)+",'"+user+"','"+user_nick+"','"+channel+"',strftime('%Y-%m-%d-%H-%M'),'"+user_message+"'"+"""
                                            )
                                    """
                                    cur.execute(sql)
                                    conn.commit()
                                    cur.close()
                                    self.send_message_to_channel( ("Message to "+user_nick+" has been sent. He will recieve it as soon as he is back"), channel)
                    else:
                        self.send_message_to_channel( ("You can use ]later only on a channel"), user)
            if ( len(command) == 2):
                if (command[0] == "register"):
                    if not re.search("^#", channel):
                        conn = sqlite3.connect('../db/register.db')
                        cur = conn.cursor()
                        sql = """SELECT * FROM register
                                WHERE user = '"""+user+"'"+"""
                        """
                        cur.execute(sql)
                        conn.commit()
                        row = []
                        for row in cur:
                            pass    
                        cur.close()
                        if user not in row:
                            self.send_message_to_channel( ("You are not allowed to register, please contact more privileged user"), user)
                        else:   #user found in 'register' database
                            ifowner = row[3]
                            if ifowner == 0:    #it not 'owner' type of users
                                if row[2] == None:  #password field is empty - this user is set to be registered by owner
                                    user_password = command[1]
                                    pass_to_db = hashlib.md5( user_password.encode('utf-8') ).hexdigest()
                                    conn = sqlite3.connect('../db/register.db')
                                    cur = conn.cursor()
                                    sql = """UPDATE register
                                            SET pass = '"""+str(pass_to_db)+"'"+"""
                                            WHERE user = '"""+user+"'"+"""
                                    """
                                    cur.execute(sql)
                                    conn.commit()
                                    cur.close()
                                    self.send_message_to_channel( ("Congratulations! You are registered. Don't forget your password, you need it to authenticate with ]login"), user)
                                else:
                                    self.send_message_to_channel( ("You are already registered"), user)
                if (command[0] == "login"):
                    if not re.search("^#", channel):
                        conn = sqlite3.connect('../db/register.db')
                        cur = conn.cursor()
                        sql = """SELECT * FROM register
                                WHERE user = '"""+user+"'"+"""
                        """
                        cur.execute(sql)
                        conn.commit()
                        row = []
                        for row in cur:
                            pass
                        cur.close()
                        if user not in row:
                            self.send_message_to_channel( ("You are not registered!"), user)
                        else:
                            if row[2] == None:
                                self.send_message_to_channel( ("You are not registered!"), user)
                            else:   #he is registered
                                if row[4] == 1:
                                    self.send_message_to_channel( ("You are already authenticated!"), user)
                                else:
                                    user_password = command[1]
                                    user_password_hash = hashlib.md5( user_password.encode('utf-8') ).hexdigest()
                                    user_password_hash_in_db = row[2]
                                    if str(user_password_hash) == str(user_password_hash_in_db):    #password matches
                                        conn = sqlite3.connect('../db/register.db')
                                        cur = conn.cursor()
                                        sql = """UPDATE register
                                                SET authenticated = 1
                                                WHERE user = '"""+user+"'"+"""
                                        """
                                        cur.execute(sql)
                                        conn.commit()
                                        cur.close()
                                        self.send_message_to_channel( ("Successful!"), user)
                                    else:
                                        self.send_message_to_channel( ("Password incorrect!"), user)
                if (command[0] == "if"):
                    nick = command[1]
                    conn = sqlite3.connect('../db/users.db')
                    cur=conn.cursor()
                    sql = """SELECT * FROM users
                            WHERE user = '"""+nick+"'"+"""
                    """
                    cur.execute(sql)
                    conn.commit()
                                    
                    row = []
                    for row in cur:
                        pass
                    cur.close()
                    if nick not in row:
                        if re.search("^#", channel):
                            self.send_message_to_channel( ("False"), channel)
                        else:
                            self.send_message_to_channel( ("False"), user)
                    else:
                        if re.search("^#", channel):
                            self.send_message_to_channel( ("True"), channel)
                        else:
                            self.send_message_to_channel( ("True"), user)
                if (command[0] == "add"):
                    if ( admin != 'True' ):
                        if re.search("^#", channel):
                            self.send_message_to_channel( ("Your don't have permissions for this command"), channel)
                        else:
                            self.send_message_to_channel( ("Your don't have permissions for this command"), user)
                    
                if (command[0] == "games"):
                    os.system("wget http://master.open-ra.org/list.php > /dev/null 2>&1")
                    filename = 'list.php'
                    file = open(filename, 'r')
                    lines = file.readlines()
                    file.close()
                    os.system("rm list.php")
                    length = len(lines)
                    if length == 1:
                        if re.search("^#", channel):
                            self.send_message_to_channel( ("No games found"), channel)
                        else:
                            self.send_message_to_channel( ("No games found"), user)
                    else:   # there are one or more games
                        if (command[1] == "1"):
                            length = length / 9 # number of games
                            a1=2
                            loc=3
                            a2=4
                            a3=5
                            a4=7
                            for i in range(int(length)):
                                if lines[a2].lstrip().rstrip() == 'State: 1':
                                    state = '(W)'
                                    ### for location
                                    ip=lines[loc].split(':')[1].lstrip()    # ip address
                                    os.system("whois "+ip+" > whois_info")
                                    time.sleep(1)
                                    filename = 'whois_info'
                                    file = open(filename,'r')
                                    who = file.readlines()
                                    file.close()
                                    a =  str(who).split()
                                    try:
                                        index = a.index('\'country:')
                                        index = int(index) + 1
                                        code = a[index]
                                        code = code[:-4].upper()    #got country code
                                        code_index = codes.index(code)
                                        country = match_codes[code_index]
                                    except:
                                        country = 'USA'
                                    sname = lines[a1].encode('utf-8').decode('utf-8')
                                    sname = str(sname)
                                    games = '@ '+sname.lstrip().rstrip()[6:].lstrip().ljust(25)+' - '+state+' - '+lines[a3].lstrip().rstrip()+' - '+lines[a4].lstrip().rstrip().split(' ')[1]+' - '+country
                                    a1=a1+9
                                    loc=loc+9
                                    a2=a2+9
                                    a3=a3+9
                                    a4=a4+9
                                    if re.search("^#", channel):
                                        self.send_message_to_channel( (games), channel )
                                    else:
                                        self.send_message_to_channel( (games), user )
                        elif (command[1] == "2"):
                            length = length / 9 # number of games
                            a1=2
                            loc=3
                            a2=4
                            a3=5
                            a4=7
                            for i in range(int(length)):
                                if lines[a2].lstrip().rstrip() == 'State: 2':
                                    state = '(P)'
                                    ### for location
                                    ip=lines[loc].split(':')[1].lstrip()    # ip address
                                    os.system("whois "+ip+" > whois_info")
                                    time.sleep(1)
                                    filename = 'whois_info'
                                    file = open(filename,'r')
                                    who = file.readlines()
                                    file.close()
                                    a =  str(who).split()
                                    try:
                                        index = a.index('\'country:')
                                        index = int(index) + 1
                                        code = a[index]
                                        code = code[:-4].upper()    #got country code
                                        code_index = codes.index(code)
                                        country = match_codes[code_index]
                                    except:
                                        country = 'USA'
                                    sname = lines[a1].encode('utf-8').decode('utf-8')
                                    sname = str(sname)
                                    games = '@ '+sname.lstrip().rstrip()[6:].lstrip().ljust(25)+' - '+state+' - '+lines[a3].lstrip().rstrip()+' - '+lines[a4].lstrip().rstrip().split(' ')[1]+' - '+country
                                    a1=a1+9
                                    loc=loc+9
                                    a2=a2+9
                                    a3=a3+9
                                    a4=a4+9
                                    if re.search("^#", channel):
                                        self.send_message_to_channel( (games), channel )
                                    else:
                                        self.send_message_to_channel( (games), user )
                        else:   #it is pattern
                            chars=['*','.','$','^','@','{','}','+','?']
                            for i in range(int(len(chars))):
                                if chars[i] in command[1]:
                                    check = 'tru'
                                    break
                                else:
                                    check = 'fals'
                            if check == 'fals':
                                p = re.compile(command[1], re.IGNORECASE)
                                length = length / 9 # number of games
                                a1=2
                                loc=3
                                a2=4
                                a3=5
                                a4=7
                                for i in range(int(length)):
                                    if p.search(lines[a1]):
                                        if lines[a2].lstrip().rstrip() == 'State: 1':
                                            state = '(W)'
                                        elif lines[a2].lstrip().rstrip() == 'State: 2':
                                            state = '(P)'
                                        ### for location
                                        ip=lines[loc].split(':')[1].lstrip()    # ip address
                                        os.system("whois "+ip+" > whois_info")
                                        time.sleep(1)
                                        filename = 'whois_info'
                                        file = open(filename,'r')
                                        who = file.readlines()
                                        file.close()
                                        a =  str(who).split()
                                        try:
                                            index = a.index('\'country:')
                                            index = int(index) + 1
                                            code = a[index]
                                            code = code[:-4].upper()    #got country code
                                            code_index = codes.index(code)
                                            country = match_codes[code_index]
                                        except:
                                            country = 'USA'
                                        sname = lines[a1].encode('utf-8').decode('utf-8')
                                        sname = str(sname)
                                        games = '@ '+sname.lstrip().rstrip()[6:].lstrip()+' - '+state+' - '+lines[a3].lstrip().rstrip()+' - '+lines[a4].lstrip().rstrip().split(' ')[1]+' - '+country
                                        if re.search("^#", channel):
                                            self.send_message_to_channel( (games), channel)
                                        else:
                                            self.send_message_to_channel( (games), user)
                                        break
                                    a1=a1+9
                                    loc=loc+9
                                    a2=a2+9
                                    a3=a3+9
                                    a4=a4+9                 
#           if re.search('http://*', command):
#               length = len(command)
#               for i in range(int(length)):
#                   if re.search('http://*', command[i]):
#                       link = command[i]
#                       break
#               os.system("wget "+link)
#               part = len(link.split('//'))        
#               if part == 2:
#                   filename = 'index.html'
#                   file = open(filename, 'r')
#                   lines = file.readlines()
    
            if ( len(command) == 1):
                if (command[0] == "online"):
                    if not re.search("^#", channel):
                        conn = sqlite3.connect('../db/register.db')
                        cur = conn.cursor()
                        sql = """SELECT * FROM register
                                WHERE authenticated = 1
                        """
                        cur.execute(sql)
                        conn.commit()
                        row = []
                        online = []
                        for row in cur:
                            online.append(row)
                        cur.close()
                        actual = []
                        for i in range(int(len(online))):
                            actual.append(online[i][1])
                        num_users_online = int(len(actual))
                        if num_users_online == 0:
                            self.send_message_to_channel( ("No any authenticated users online"), user)
                        else:
                            usrs = ", ".join(actual)
                            self.send_message_to_channel( (str(num_users_online)+" authenticated users online: "+usrs), user)
                if (command[0] == "hi"):
                    if re.search("^#", channel):
                        self.send_message_to_channel( ("Hello, " + user), channel )
                    else:
                        self.send_message_to_channel( ("Hello, " + user), user)
                if (command[0] == "tr"):
                    self.send_message_to_channel( ("Usage: ]tr <from language> <to language> <text to translate>   |   To get a list of the available languages in private: ]langs   |   For example, to translate from English to German: ]tr en de Thank you"), user)
                if (command[0] == "langs"):
                    b=0
                    for i in range(25):
                        line1 = languages[b].ljust(8)+real_langs[b].ljust(20)
                        b=b+1
                        line2 = languages[b].ljust(8)+real_langs[b].ljust(20)
                        line_output=line1+'| '+line2
                        time.sleep(1)
                        self.send_message_to_channel( (line_output), user)
                        b=b+1
                        if b == 50:
                            break
                if (command[0] == "games"):
                    try:
                        os.system("wget http://master.open-ra.org/list.php > /dev/null 2>&1")
                        filename = "list.php"
                        file = open(filename, 'r')
                        lines = file.readlines()    #got a list
                        file.close()
                        os.system("rm list.php")
                        length = len(lines)
                        if length == 1:
                            if re.search("^#", channel):
                                self.send_message_to_channel( ("No games found"), channel )
                            else:
                                self.send_message_to_channel( ("No games found"), user )
                        else:
                            length = length / 9
                            a1=2
                            loc=3
                            a2=4
                            a3=5
                            a4=7
                            games=''
                            count='0'
                            for i in range(int(length)):
                                if lines[a2].lstrip().rstrip() == 'State: 1':
                                    count='1'   # lock - there are games in State: 1
                                    state = '(W)'
                                    ### for location
                                    ip=lines[loc].split(':')[1].lstrip()    # ip address
                                    os.system("whois "+ip+" > whois_info")
                                    time.sleep(0.4)
                                    filename = 'whois_info'
                                    file = open(filename,'r')
                                    who = file.readlines()
                                    file.close()
                                    a =  str(who).split()
                                    try:
                                        index = a.index('\'country:')
                                        index = int(index) + 1
                                        code = a[index]
                                        code = code[:-4].upper()    #got country code
                                        code_index = codes.index(code)
                                        country = match_codes[code_index]   #got country name
                                    except:
                                        country = 'USA' #whois does not show coutry code for most USA IPs and some Canadians (did not find a way to determine where USA and where Canada is)
                                    sname = lines[a1].encode('utf-8').decode('utf-8')
                                    sname = str(sname)
                                    games = sname.lstrip().rstrip()[6:].lstrip().ljust(25)+' - '+state+' - '+lines[a3].lstrip().rstrip()+' - '+lines[a4].lstrip().rstrip().split(' ')[1]+' - '+country
                                    if re.search("^#", channel):
                                        self.send_message_to_channel( (games), channel )
                                    else:
                                        self.send_message_to_channel( (games), user )
                                a1=a1+9 
                                loc=loc+9
                                a2=a2+9
                                a3=a3+9
                                a4=a4+9
                            if count == "0":    #appeared no games in State: 1
                                if re.search("^#", channel):
                                    self.send_message_to_channel( ("No games waiting for players found"), channel )
                                else:
                                    self.send_message_to_channel( ("No games waiting for players found"), user )
                    except:
                        exc = ']games crashed\n'
                        filename = 'except_log.txt'
                        file = open(filename, 'a')
                        file.write(exc)
                        file.close()
                        
            else:
                if (command[0] == "bop"):
                    self.send_message_to_channel( ("\x01ACTION bopz " + str(command[1]) + "\x01"), channel )

def main():
    # Here begins the main programs flow:
    test2 = IRC_Server("irc.freenode.net", 6667, "orabot", "#openra")
    test = IRC_Server("irc.freenode.net", 6667, "orabot", "##untitled")
    run_test = multiprocessing.Process(None,test.connect )
    run_test.start()
    try:
        while(test.should_reconnect):
            time.sleep(5)
        run_test.join()
    except KeyboardInterrupt: # Ctrl + C pressed
        pass # We're ignoring that Exception, so the user does not see that this Exception was raised.
    #if run_test.is_alive():
    #   print("Terminating process ...")
    #   run_test.terminate()    # Terminate process
    print("Bot exited.")