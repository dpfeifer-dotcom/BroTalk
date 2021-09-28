import threading
import socket
import messageIO
from datetime import datetime


host = 'localhost'
port = 20000
file_port = 20001
key = b'BrmfEQubZRCs2KghS0W4WmmnQ7atq8-QieM3qo-_Xec='

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen(5)

file_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
file_server.bind((host, file_port))
file_server.listen(5)

TEXT_BUFFER_SIZE = 1024
FILE_BUFFER_SIZE = 10485760

clients = []
nicknames = []
addresses = []
file_clients = []
file_nicknames = []
file_addresses = []


def broadcast(message_pick, sender_addr, address):
    if address == 'GLOBAL':
        for client in clients:
            if client != sender_addr:
                client.send(message_pick)
    else:
        try:
            index = nicknames.index(address)
            client = clients[index]
            client.send(message_pick)
        except:
            message_fail_pick = messageIO.send_krypt('MSG', 'SERVER', '', address + ' is not available!', key)
            sender_addr.send(message_fail_pick)


def file_pre_broadcast(message_pick, file_name, sender_addr, address):
    try:
        index = nicknames.index(address)
        file_client = file_clients[index]
        file_message_pick = messageIO.send_krypt('MSG', sender_addr, '', file_name, key)
        file_client.send(file_message_pick)
    except:
        message_fail_pick = messageIO.send_krypt('MSG', 'SERVER', '', address + ' is not available!', key)
        sender_addr = clients[nicknames.index(sender_addr)]
        sender_addr.send(message_fail_pick)


def file_broadcast(file_message_pick, file_name, sender_addr, address):
    index = nicknames.index(address)
    file_client = file_clients[index]
    file_client.send(file_message_pick)


def handle(client):
    while True:
        try:
            message_pick = client.recv(TEXT_BUFFER_SIZE)
            message_pick = messageIO.read_krypt(message_pick, key)
            command = message_pick['cmd']
            sender = message_pick['sender']
            address = message_pick['address']
            data = message_pick['data']
            sender_addr = clients[nicknames.index(sender)]
            if command == 'TEAM':
                sender = 'SERVER'
                data = ', '.join(nicknames)
            message_pick = messageIO.send_krypt(command, sender, address, data, key)
            broadcast(message_pick, sender_addr, address)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            message_left_pick = messageIO.send_krypt('MSG', 'SERVER', 'GLOBAL', f'{nickname} left the Bros!', key)
            print(
                f'{datetime.now().strftime("(%Y.%m.%d %H:%M:%S)")} Talk Server disconnected with {nickname} {str(addresses[index])}')
            broadcast(message_left_pick, 'SERVER', 'GLOBAL')
            nicknames.remove(nickname)
            address = addresses[index]
            addresses.remove(address)
            break


def file_handle(file_client):
    while True:
        try:
            file_message_pick = file_client.recv(TEXT_BUFFER_SIZE)
            file_message_pick = messageIO.read_data_krypt(file_message_pick, key)
            file_sender = file_message_pick['sender']
            file_address = file_message_pick['address']
            file_name = file_message_pick['data']
            file_pre_broadcast(file_message_pick, file_name, file_sender, file_address)
            print(f'{datetime.now().strftime("(%Y.%m.%d %H:%M:%S)")} START File ({file_name}) transfer to {file_address} from {file_sender}')
            file_message_pick = file_client.recv(FILE_BUFFER_SIZE)
            file_broadcast(file_message_pick, file_name, file_sender, file_address)
            if len(file_message_pick) < FILE_BUFFER_SIZE:
                print(f'{datetime.now().strftime("(%Y.%m.%d %H:%M:%S)")} FINISHED File ({file_name}) transfer to {file_address} from {file_sender}')
                continue
            while True:
                file_message_pick = file_client.recv(FILE_BUFFER_SIZE)
                file_broadcast(file_message_pick, file_name, file_sender, file_address)
                if len(file_message_pick) < FILE_BUFFER_SIZE:
                    print(f'{datetime.now().strftime("(%Y.%m.%d %H:%M:%S)")} FINISHED File ({file_name}) transfer to {file_address} from {file_sender}')
                    break

        except:
            index = file_clients.index(file_client)
            file_clients.remove(file_client)
            file_client.close()
            file_address = file_addresses[index]
            file_addresses.remove(file_address)
            file_nickname = file_nicknames[index]
            file_nicknames.remove(file_nickname)
            print(
                f'{datetime.now().strftime("(%Y.%m.%d %H:%M:%S)")} File Server disconnected with {file_nickname} {file_address}')
            break


def receive():
    while True:
        client, address = server.accept()
        file_client, file_address = file_server.accept()
        print(f'{datetime.now().strftime("(%Y.%m.%d %H:%M:%S)")} Talk Server Connected with {str(address)}')
        print(f'{datetime.now().strftime("(%Y.%m.%d %H:%M:%S)")} File Server Connected with {str(file_address)}')
        message_welcome_pick = messageIO.send_krypt('NICK', 'SERVER', 'GLOBAL', '', key)
        client.send(message_welcome_pick)
        nickname_pick = client.recv(TEXT_BUFFER_SIZE)
        nickname_pack = messageIO.read_krypt(nickname_pick, key)
        nickname = nickname_pack['sender']

        nicknames.append(nickname)
        clients.append(client)
        addresses.append(address)
        file_nicknames.append(nickname)
        file_clients.append(file_client)
        file_addresses.append(file_address)

        print(f'{datetime.now().strftime("(%Y.%m.%d %H:%M:%S)")} Nickname of the client is {nickname}!')

        message_join_pick = messageIO.send_krypt('MSG', 'SERVER', 'GLOBAL', f'{nickname} joined the BroTalk!', key)
        broadcast(message_join_pick, client, 'GLOBAL')

        message_greetings_pick = messageIO.send_krypt('MSG', 'SERVER', 'GLOBAL', 'Welcome to the BroTalk!', key)
        client.send(message_greetings_pick)

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()
        file_thread = threading.Thread(target=file_handle, args=(file_client,))
        file_thread.start()


print('The GrandMAsterBro is listening...')
receive()
