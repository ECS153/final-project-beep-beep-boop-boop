
from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64
import os.path


# refer to https://pycryptodome.readthedocs.io/en/latest/src/examples.html#generate-public-key-and-private-key
# for encrypting / decrypting (see the RSA session)

# refer to https://flask-socketio.readthedocs.io/en/latest/
# for flask socketio


PATH_PRIVATE_KEY = "private.pem"
PATH_PUBLIC_KEY = "public.pem"
KEY_ENCODING_EXTENSION = "PEM"

app = Flask(__name__)
app.config['SECRET KEY'] = 'beepbeepboopboop2020beerflu'
socketio = SocketIO(app)


# Encryption #
class Keys:  # since python doesn't support private, try to only use the method to access variable to avoid mistakes.
    __private_key = None
    __public_key = None
    __singleton = None

    def __init__(self):
        if Keys.__singleton is not None:
            raise Exception("This class is a singleton!")
        else:
            if os.path.exists(PATH_PRIVATE_KEY) and os.path.exists(PATH_PUBLIC_KEY):
                self.__private_key = RSA.import_key(open(PATH_PRIVATE_KEY).read())
                self.__public_key = RSA.import_key(open(PATH_PUBLIC_KEY).read())
            else:  # create new set of keys
                key = RSA.generate(2048)
                self.__private_key = key.export_key(KEY_ENCODING_EXTENSION)
                self.__public_key = key.publickey().export_key(KEY_ENCODING_EXTENSION)
                outf = open(PATH_PRIVATE_KEY, "wb")
                outf.write(self.__private_key)
                outf.close()
                outf = open(PATH_PUBLIC_KEY, "wb")
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


# SocketIO #
@app.route('/')
def sessions():
    return render_template('website.html')


@socketio.on('request_public_key')
def handle_public_key_request(methods=['GET', 'POST']):
    print(Keys.getPublicKey().export_key())
    send(Keys.getPublicKey().export_key())


@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=ack)


def ack(methods=['GET', 'POST']):
    print('message was received!!!')


def main():
    socketio.run(app, debug=True)


if __name__ == '__main__':
    main()
