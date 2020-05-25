
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, close_room, disconnect
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import base64
import os.path
import json
import settings


# https://stackoverflow.com/questions/45918818/how-to-send-message-from-server-to-client-using-flask-socket-io


# refer to https://pycryptodome.readthedocs.io/en/latest/src/examples.html#generate-public-key-and-private-key
# for encrypting / decrypting (see the RSA session)

# refer to https://flask-socketio.readthedocs.io/en/latest/
# for flask socketio

app = Flask(__name__)
app.config['SECRET KEY'] = settings.APP_SECRET_KEY
socketio = SocketIO(app, ping_interval=settings.PING_INTERVAL, ping_timeout=settings.PING_TIMEOUT)


# Encryption #
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


# SocketIO #
client = {}
socket = {}  # username as key, sid as value
socket_inv = {}  # sid as value, username as key


@app.route('/')
def sessions():
    return render_template('website.html')


@socketio.on('connect')
def handle_connect():
    print('Client connected')


@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in socket_inv:  # disconnected from timeout
        print("Client disconnected from timeout")
        username = socket_inv.pop(request.sid)
        socket.pop(username)
        client.pop(username)
    else:
        print("Client disconnected by server")


@socketio.on('join')
def assign_private_room(data):
    if data['username'] in socket:  # user already logged in somewhere, disable previous room
        sid = socket.pop(data['username'])
        socket_inv.pop(sid)
        close_room(sid)

    join_room(request.sid)
    client[data['username']] = {
        'nickname': data['nickname'],
        'public_key': data['public_key']
    }
    socket[data['username']] = request.sid  # 'a' is username
    socket_inv[request.sid] = data['username']
    distribute_user_list()
    emit('public key', {"public_key": Keys.getPublicKey().export_key(settings.KEY_ENCODING_EXTENSION)})


@socketio.on('update')
def update_client(data):
    client[data['username']]['nickname'] = data['nickname']


@socketio.on('request user list')
def distribute_user_list():
    emit('user list', json.loads(json.dumps(client)))


@socketio.on('message')
def handle_messages(data):
    # json in this format:
    # { 'message': '...encrypted...', 'recipient_username': 'username' }
    print(data);
    emit('message', data, room=socket[data['recipient']])

    # FIXME: when we do mixnet
    # onion layer should goes as follows: ( ) indicates client encryption, < > indicates server encryption
    # < < < < < ( message, sender ), recipient, this server >, mixnet server 2 >, mixnet server 1 >, this server >
    # client should be given list of all the mixnet server IP and public key and create this route
    #
    # http request to recipient server, then each mixnet server peel off a layer
    # when it comes back to this server, emit('message', data, room=socket[data['recipient']])


def main():
    # data = "I am a potato who is eating potato from a potato plant in a potato farm."
    # encrypted_data = encrypt(data.encode("utf-8"), Keys.getPublicKey())
    # decrypted_data = decrypt(encrypted_data)
    #
    # print("************Encryption Test***************")
    # print("Original: ", data)
    # print("***************************")
    # print("Encrypted: ", encrypted_data)
    # print("***************************")
    # print("Decrypted: ", decrypted_data)
    # print("***************************")

    socketio.run(app, port=settings.PORT, debug=settings.DEBUG_MODE)


if __name__ == '__main__':
    main()
