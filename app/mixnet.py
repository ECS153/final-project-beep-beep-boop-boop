
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from RSA_script import *
import settings
import json
import server_list
import requests


app = Flask(__name__)
app.config['SECRET KEY'] = settings.APP_SECRET_KEY
socketio = SocketIO(app, ping_interval=100000, ping_timeout=100000)
key = Keys()


@app.route('/getServerPublicKey', methods=['GET'])
def get_public_key():
    # data = request.get_data()
    # url = 'https://' + data['recipient'] + '/key'
    # requests.post(url, data=RSA_script.Keys.getPublicKey().export_key(settings.KEY_ENCODING_EXTENSION), verify=False)
    return Keys().getPublicKey().export_key(settings.KEY_ENCODING_EXTENSION)


@app.route('/incoming', methods=['POST'])
def handle_incoming_package():
    package = json.loads(request.get_data())
    # print("Encrypted Message After Post:")
    # print(data)
    item = package.pop()
    encoded = encode_array(item)
    recipient = decrypt(encoded, key.getPrivateKey())
    # print(recipient)
    url = 'https://' + recipient + '/incoming'
    requests.post(url, data=json.dumps(package), verify=False)
    return 'Success'


@app.route('/incoming', methods=['POST'])
def handle_incoming_packageV2():
    package = json.loads(request.get_data())
    # print("Encrypted Message After Post:")
    # print(data)
    encoded = encode_array(package)
    decrypted = decrypt(encoded, key.getPrivateKey())
    # print(decrypted['recipient'])
    url = 'https://' + decrypted['recipient'] + '/incoming'
    requests.post(url, data=json.dumps(decrypted['encrypted']), verify=False)
    return 'Success'


def main():
    socketio.run(app, host='0.0.0.0', port=settings.PORT, debug=settings.DEBUG_MODE, ssl_context=('cert.pem', 'key.pem'))


if __name__ == '__main__':
    main()
