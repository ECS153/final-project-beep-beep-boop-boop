
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import os.path
import settings

# refer to https://pycryptodome.readthedocs.io/en/latest/src/examples.html#generate-public-key-and-private-key
# for encrypting / decrypting (see the RSA session)


class Keys:  # since python doesn't support private, try to only use the method to access variable to avoid mistakes.
    __private_key = None
    __public_key = None
    __singleton = None

    def __init__(self):
        if Keys.__singleton is not None:
            raise Exception("This class is a singleton!")
        else:
            if os.path.exists(settings.PATH_PRIVATE_KEY) and os.path.exists(settings.PATH_PUBLIC_KEY):
                self.__private_key = RSA.import_key(open(settings.PATH_PRIVATE_KEY).read())
                self.__public_key = RSA.import_key(open(settings.PATH_PUBLIC_KEY).read())
            else:  # create new set of keys
                key = RSA.generate(2048)
                self.__private_key = key.export_key(settings.KEY_ENCODING_EXTENSION)
                self.__public_key = key.publickey().export_key(settings.KEY_ENCODING_EXTENSION)
                outf = open(settings.PATH_PRIVATE_KEY, "wb")
                outf.write(self.__private_key)
                outf.close()
                outf = open(settings.PATH_PUBLIC_KEY, "wb")
                outf.write(self.__public_key)
                outf.close()

            Keys.__singleton = self

    @staticmethod
    def getPublicKey():
        if Keys.__singleton is None:
            Keys()

        return Keys.__singleton.__public_key

    @staticmethod
    def getPrivateKey():
        if Keys.__singleton is None:
            Keys()

        return Keys.__singleton.__private_key


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


def decrypt(encoded_data):
    private_key = RSA.import_key(open("private.pem").read())
    enc_session_key, nonce, tag, ciphertext = encoded_data

    # Decrypt the session key with the private RSA key
    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(enc_session_key)

    # Decrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    data = cipher_aes.decrypt_and_verify(ciphertext, tag)
    return data.decode("utf-8")