from cryptography.fernet import Fernet


def encoding(key, text):
    cipher_suite = Fernet(key)
    if type(text) is not bytes:
        text = text.encode('utf-8')
    cipher_text = cipher_suite.encrypt(text)
    return cipher_text


def decoding(key, text):
    cipher_suite = Fernet(key)
    plain_text = cipher_suite.decrypt(text)
    return plain_text


def gen_encrypt_key():
    key = Fernet.generate_key()
    return key

