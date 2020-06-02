from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, close_room, disconnect
import json
from RSA_script import *
import server_list
import settings
import requests
import base64
import re

# https://stackoverflow.com/questions/45918818/how-to-send-message-from-server-to-client-using-flask-socket-io

# refer to https://flask-socketio.readthedocs.io/en/latest/
# for flask socketio


hosting_address = '127.0.0.1:5000'
app = Flask(__name__)
app.config['SECRET KEY'] = settings.APP_SECRET_KEY
socketio = SocketIO(app, ping_interval=settings.PING_INTERVAL, ping_timeout=settings.PING_TIMEOUT)
key = Keys()
client = {}
socket = {}  # username as key, sid as value
socket_inv = {}  # sid as value, username as key
online_mixnets = {}


@app.route('/')
def sessions():
    return render_template('website.html')


@app.route('/handle_incoming_package', methods=['POST'])
def handle_incoming_package():
    package = request.get_data()
    item = package.pop()
    encoded = encode_item(item)
    decrypted = decrypt(encoded, key.getPrivateKey())

    if decrypted['real_package']:
        emit('message', decrypted['encrypted'], room=socket[decrypted['recipient']])


@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('public key', key.getPublicKey().export_key(settings.KEY_ENCODING_EXTENSION))
    # print(online_mixnets)
    emit('online mixnet server', list(online_mixnets.keys()))


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
        emit('disconnect', data,
             room=socket[data['username']])  # to let client know, actual disconnect will happen from timeout
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
    emit('connected')


@socketio.on('update')
def update_client(data):
    client[data['username']]['nickname'] = data['nickname']


@socketio.on('request user list')
def distribute_user_list():
    emit('user list', json.loads(json.dumps(client)))


@socketio.on('message')
def handle_messages(data):
    if len(data['recipient']) == 1:
        emit('message', data['encrypted'], room=socket[data['recipient'][0]])
    else:
        recipient_id = data['recipient'].pop(0)

        item = {
            "recipient": recipient_id,
            "real_package:": True
        }

        package = [decode_item(data['encrypted']),
                   decode_array(encrypt(json.dumps(item).encode("utf-8"), key.getPublicKey()))]

        print('*******************')
        print(package[1][0])
        print('*******************', type(package[1][0]))
        print(encode_array(package[1]))
        print('*******************', type(encode_array(package[1])))

        for i in range(len(data['recipient'])):
            item = data['recipient'][i]

            if i + 1 != len(data['recipient']):
                recipient_key = Keys(online_mixnets[data['recipient'][i+1]])
                item = decode_array(encrypt(item.encode("utf-8"), recipient_key.getPublicKey()))

            package.append(item)


        url = 'https://' + package.pop() + '/handle_incoming_package'
        requests.post(url, data=json.dumps(package), verify=False)


def json_n_encode(data):
    return json.dumps(data).encode("utf-8")


def main():
    # print("Before for")
    for server_address in server_list.SERVERS:
        # print("In for")
        if server_address != hosting_address:
            try:
                url = 'https://' + server_address + '/getServerPublicKey'
                response = requests.get(url, verify=False)
                online_mixnets[server_address] = response.text
            except requests.exceptions.ConnectionError:
                print(server_address + " is down.")
                pass
    socketio.run(app, host='0.0.0.0', port=settings.PORT, debug=settings.DEBUG_MODE)
    # socketio.run(app, host='0.0.0.0', port=settings.PORT, debug=settings.DEBUG_MODE, ssl_context=('cert.pem', 'key.pem'))


if __name__ == '__main__':
    main()