
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from RSA_script import *
import settings
import json
import sys
import requests


app = Flask(__name__)
app.config['SECRET KEY'] = settings.APP_SECRET_KEY
socketio = SocketIO(app, ping_interval=100000, ping_timeout=100000)
key = Keys()


@app.route('/getServerPublicKey', methods=['GET'])
def get_public_key():
    return key.getPublicKey().export_key(settings.KEY_ENCODING_EXTENSION)


@app.route('/handle_incoming_package', methods=['POST'])
def handle_incoming_packageV2():
    package = json.loads(request.get_data())
    encoded = encode_array(package)
    decrypted = json.loads(decrypt(encoded, key.getPrivateKey()))
    print(decrypted)
    url = 'http://' + decrypted['recipient'] + '/handle_incoming_package'
    try:
        requests.post(url, data=json.dumps(decrypted['encrypted']), timeout=0.0001)
    except requests.exceptions.ReadTimeout:
        pass
    return 'Success'


def main():
    if len(sys.argv) != 2:
        print("python3 mixnet.py <port>")
        exit()

    socketio.run(app, host='0.0.0.0', port=sys.argv[1], debug=settings.DEBUG_MODE)


if __name__ == '__main__':
    main()
