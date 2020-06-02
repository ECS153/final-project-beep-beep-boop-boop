from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import os.path
import settings
import base64


# refer to https://pycryptodome.readthedocs.io/en/latest/src/examples.html#generate-public-key-and-private-key
# for encrypting / decrypting (see the RSA session)


class Keys:  # since python doesn't support private, try to only use the method to access variable to avoid mistakes.
    __private_key = None
    __public_key = None

    def __init__(self, public_pem=None):
        if not public_pem:
            key = RSA.generate(2048)
            self.__private_key = key
            self.__public_key = key.publickey()
        else:
            if public_pem:
                self.__public_key = RSA.import_key(public_pem)

    def getPublicKey(self):
        return self.__public_key

    def getPrivateKey(self):
        return self.__private_key


def encrypt(data, public_key):
    session_key = get_random_bytes(16)

    # Encrypt the session key with the public RSA key
    cipher_rsa = PKCS1_OAEP.new(public_key)
    enc_session_key = cipher_rsa.encrypt(session_key)

    # Encrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(data)
    encoded = [x for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext)]
    return encoded


def decrypt(encoded_data, private_key):
    enc_session_key, nonce, tag, ciphertext = encoded_data

    # Decrypt the session key with the private RSA key
    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(enc_session_key)

    # Decrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    data = cipher_aes.decrypt_and_verify(ciphertext, tag)
    return data.decode("utf-8")


def decode_array(array):
    result = []
    for x in array:
        result.append(base64.b64encode(x).decode())
    return result


def encode_array(array):
    result = []
    for x in array:
        result.append(base64.decodebytes(x.encode()))
    return result


def decode_item(byte):
    return base64.b64encode(byte).decode()


def encode_item(byte):
    return base64.decodebytes(byte.encode())