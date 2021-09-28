import socket
import threading
import messageIO
import pickle
import os
import BroKrypt
from playsound import playsound
from datetime import datetime
import random
from time import sleep
import openfile


def receive():
    while True:
        try:
            message_pick = client.recv(TEXT_BUFFER_SIZE)
            message_pack = messageIO.read_krypt(message_pick, key)
            if message_pack['cmd'] == 'NICK':
                client.send(nickname_pick)
            elif message_pack['cmd'] == 'ALERT':
                choice = random.choice(alert_sounds)
                sound = choice['sound']
                text = choice['text']
                sound_thread = threading.Thread(target=play_wav, args=(sound,))
                sound_thread.start()
                print(style.BLUE +
                      datetime.now().strftime("(%H:%M)"),
                      text + '...from ' +
                      message_pack['sender'] +
                      style.RESET)
            else:
                color = style.YELLOW
                if message_pack['sender'] == 'SERVER':
                    color = style.RED
                if message_pack['address'] == nickname and message_pack['sender'] != 'SERVER':
                    print(color + datetime.now().strftime("(%H:%M)"),
                          message_pack['sender'] + '[private]:',
                          message_pack['data'] + style.RESET)
                else:
                    print(color + datetime.now().strftime("(%H:%M)"),
                          message_pack['sender'] + ':',
                          message_pack['data'] + style.RESET)
        except:
            print('Hmm... something wrong')
            client.close()
            file_client.close()
            break


def write():
    while True:
        message_pack = {'cmd': 'MSG',
                        'sender': nickname,
                        'address': 'GLOBAL',
                        'data': ''}
        message = input()
        if message == '':
            continue
        elif message.split()[0] == 'TO:':
            try:
                address = message.split()[1]
                message = input(style.RED + f'Message to {address}: ' + style.RESET)
                message_pack['address'] = address
            except:
                print(style.RED + "The Bro's name is missing!" + style.RESET)
                continue
        elif message.split()[0] == 'ALERT:':
            try:
                message_pack['address'] = message.split()[1]
                message_pack['cmd'] = 'ALERT'
                message = ''
            except:
                print(style.RED + "The Bro's name is missing!" + style.RESET)
                continue
        elif message.split()[0] == 'SEND:':
            address = input(style.RED + "Bro's name: " + style.RESET)
            file_dir, file_name = openfile.openfile()
            try:
                if os.path.getsize(file_dir) <= 10485760:
                    print(style.BLUE + f'Send a ({file_name}) to {address}' + style.RESET)
                    message_pack['cmd'] = 'SEND'
                    message_pack['address'] = address
                    message_pack['data'] = file_name
                    message_pick = pickle.dumps(message_pack)
                    message_pick = BroKrypt.encoding(key, message_pick)
                    file_send(message_pick)
                    file_send_thread = threading.Thread(target=file_send,
                                                        args=(messageIO.send_data_krypt(file_name, file_dir, key),))
                    file_send_thread.start()

                else:
                    print(style.RED + 'File is too large to send! (Max size is 10MB)' + style.RESET)
                continue
            except:
                print('hello')
        elif message == 'TEAM:':
            message_pack['cmd'] = 'TEAM'
            message_pack['address'] = nickname
            message = ''

        elif message == 'LIST:':
            print(style.RED +
                  "TO: <Bro's name>    [Send private message to one/all of Bros]\n"
                  "ALERT: <Bro's name> [Send private message to one/all of Bros]\n"
                  "SEND:               [Send file one/all of Bros]\n"
                  "TEAM:               [Get list of available Bros]\n"
                  "**** If Bro's name is GLOBAL, you send it to all of Bros ****" +
                  style.RESET)
            continue
        message_pack['data'] = message
        message_pick = pickle.dumps(message_pack)
        message_pick = BroKrypt.encoding(key, message_pick)

        if len(message_pick) <= TEXT_BUFFER_SIZE:
            send(message_pick)

        else:
            print(style.RED + 'Hey Bro! The text is too long!' + style.RESET)


def play_wav(sound):
    playsound(sound)


def send(message_pick):
    client.send(message_pick)


def file_send(message_pick):
    file_client.send(message_pick)


def file_receive():
    while True:
        file_message_pick = file_client.recv(FILE_BUFFER_SIZE)
        file_message_pick = messageIO.read_data_krypt(file_message_pick, key)
        file_sender = file_message_pick['sender']
        file_name = file_message_pick['data']
        print(style.BLUE + datetime.now().strftime("(%H:%M)"), file_sender, 'send a file (' + file_name + ') for you!' +style.RESET)
        f = open('downloads/' + file_name, 'wb')
        file_message_pick = file_client.recv(FILE_BUFFER_SIZE)
        if len(file_message_pick) < FILE_BUFFER_SIZE:
            rec_data = messageIO.read_data_krypt(file_message_pick, key)
            f.write(rec_data['data'])
            f.close()
            print(style.BLUE + datetime.now().strftime("(%H:%M)"), file_name + ' downloaded from ' + file_sender + '!' + style.RESET)
        else:
            rec_data = b''
            while True:
                rec_data += file_message_pick
                file_message_pick = file_client.recv(FILE_BUFFER_SIZE)
                if len(file_message_pick) < FILE_BUFFER_SIZE:
                    rec_data += file_message_pick
                    rec_data = messageIO.read_data_krypt(rec_data, key)
                    f.write(rec_data['data'])
                    f.close()
                    print(style.BLUE + datetime.now().strftime("(%H:%M)"), file_name + ' downloaded from ' + file_sender + '!' + style.RESET)
                    break


class style:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'


os.system("color 7")
key = b'BrmfEQubZRCs2KghS0W4WmmnQ7atq8-QieM3qo-_Xec='

alert_sounds = [
    {'sound': 'Sounds/hey.wav',
     'text': 'Hey!'},
    {'sound': 'Sounds/clearing_throat.wav',
     'text': 'Khm'},
    {'sound': 'Sounds/come_on.wav',
     'text': 'Come on!'},
    {'sound': 'Sounds/hmm.wav',
     'text': 'Hmm?'}
]

host = 'localhost'
port = 20000
file_port = 20001

TEXT_BUFFER_SIZE = 1024
FILE_BUFFER_SIZE = 10485760

nickname = input("Choose a Broname: ")
nickname_pick = messageIO.send_krypt('NICK', nickname, 'GLOBAL', '', key)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
file_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try_counter = 0
while True:
    try:
        client.connect((host, port))
        file_client.connect((host, file_port))
        receive_thread = threading.Thread(target=receive, name='receive')
        file_receive_thread = threading.Thread(target=file_receive, name='file_receive')
        write_thread = threading.Thread(target=write, name='write')
        receive_thread.start()
        file_receive_thread.start()
        write_thread.start()
        break
    except:
        color = style.RED
        print(color + 'The BroTalk service is not available!' + style.RESET)
        sleep(5)
        try_counter += 1
        print('Reconnect to the BroTalk services (' + str(try_counter) + ').')
