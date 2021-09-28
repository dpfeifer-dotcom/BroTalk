import pickle
from BroKrypt import encoding, decoding


def send_nat(command, sender, address, data):
    """
    :param command: parancs küldése
    :param sender: küldő fél
    :param address: címzett
    :param data: üzenet/adat
    :return: pickle (bytestring)
    """
    msg = {'cmd': command, 'sender': sender, 'address': address, 'data': data}
    msg_pick = pickle.dumps(msg)
    return msg_pick


def read_nat(message):
    """
    :param message: pickle (bytestring)
    :return: dict
    """
    msg_pick = pickle.loads(message)
    return msg_pick


def send_krypt(command, sender, address, data, key):
    """
    :param command: parancs küldése
    :param sender: küldő fél küldése
    :param address: címzett
    :param data: üzenet/adat
    :param key: titkosító kulcs
    :return: titkosított pickle
    """
    msg = {'cmd': command, 'sender': sender, 'address': address, 'data': data}
    msg_pick = pickle.dumps(msg)
    msg_enc = encoding(key, msg_pick)
    return msg_enc


def read_krypt(message, key):
    """
    :param message: titkosított pickle bytestring
    :param key: titkosító kulcs
    :return: dict {'cmd': , 'sender': , 'address': , 'data': }
    """
    msg_dec = decoding(key, message)
    msg_pick = pickle.loads(msg_dec)
    return msg_pick


def send_data_krypt(name, data, key):
    loaded_data = open(data, "rb")
    loaded_data = loaded_data.read()
    msg = {'name': name, 'data': loaded_data}
    msg_pick = pickle.dumps(msg)
    msg_enc = encoding(key, msg_pick)
    return msg_enc


def read_data_krypt(data, key):
    msg_dec = decoding(key, data)
    msg_pick = pickle.loads(msg_dec)
    return msg_pick
