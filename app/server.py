from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, close_room, disconnect
import json
from RSA_script import *
import settings
import requests
import random
import collections
from apscheduler.schedulers.background import BackgroundScheduler

# https://stackoverflow.com/questions/45918818/how-to-send-message-from-server-to-client-using-flask-socket-io

# refer to https://flask-socketio.readthedocs.io/en/latest/
# for flask socketio


app = Flask(__name__)
app.config['SECRET KEY'] = settings.APP_SECRET_KEY
socketio = SocketIO(app, ping_interval=settings.PING_INTERVAL, ping_timeout=settings.PING_TIMEOUT)
key = Keys()
client = {}
socket = {}  # username as key, sid as value
socket_inv = {}  # sid as value, username as key
online_mixnets = {}
post_msg_queue = collections.deque()
sched = BackgroundScheduler()


@app.route('/')
def sessions():
    return render_template('website.html')


@app.route('/handle_incoming_package', methods=['POST'])
def handle_incoming_packageV2():
    package = json.loads(request.get_data())
    encoded = encode_array(package)
    decrypted = json.loads(decrypt(encoded, key.getPrivateKey()))
    print(decrypted)
    if decrypted['real_package']:
        socketio.emit('message', encode_item(decrypted['encrypted']), room=socket[decrypted['recipient']])
    return 'Success'


@socketio.on('connect')
def handle_connect():
    emit('public key', key.getPublicKey().export_key(settings.KEY_ENCODING_EXTENSION))
    emit('online mixnet server', list(online_mixnets.keys()))


@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in socket_inv:  # disconnected from timeout
        username = socket_inv.pop(request.sid)
        socket.pop(username)
        client.pop(username)



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
def handle_messagesV2(data):
    if len(data['recipient']) == 1:
        emit('message', data['encrypted'], room=socket[data['recipient'][0]])
    else:
        package = decode_array(encrypt(json.dumps({
            "encrypted": decode_item(data['encrypted']),
            "recipient": data['recipient'][0],
            "real_package": True
        }).encode("utf-8"), key.getPublicKey()))

        data['recipient'][0] = settings.MAIN_SERVER

        for i in range(len(data['recipient'])):
            if i + 1 != len(data['recipient']):
                recipient_key = Keys(online_mixnets[data['recipient'][i + 1]])
                package = decode_array(encrypt(json.dumps({
                    "encrypted": package,
                    "recipient": data['recipient'][i]
                }).encode("utf-8"), recipient_key.getPublicKey()))

        package = {
            "encrypted": package,
            "recipient": data['recipient'].pop()
        }

        post_msg_queue.append(package)


def generate_noise():
    num_fake = random.randint(1, 2) * (len(post_msg_queue) + 1)

    for _ in range(num_fake):
        online_mixnets_address = list(online_mixnets.keys())
        random.shuffle(online_mixnets_address)
        recipient = [settings.MAIN_SERVER]
        recipient.extend(online_mixnets_address)

        package = decode_array(encrypt(json.dumps({
            "encrypted": decode_array(encrypt("beepbeepboopboop".encode("utf-8"), key.getPublicKey())),
            "recipient": "",
            "real_package": False
        }).encode("utf-8"), key.getPublicKey()))

        for i in range(len(recipient)):
            if i + 1 != len(recipient):
                recipient_key = Keys(online_mixnets[recipient[i + 1]])
                package = decode_array(encrypt(json.dumps({
                    "encrypted": package,
                    "recipient": recipient[i]
                }).encode("utf-8"), recipient_key.getPublicKey()))

        package = {
            "encrypted": package,
            "recipient": recipient.pop()
        }

        post_msg_queue.append(package)


def send_queued_message():
    generate_noise()
    random.shuffle(post_msg_queue)
    while post_msg_queue:
        package = post_msg_queue.popleft()
        # print(package)
        url = 'http://' + package['recipient'] + '/handle_incoming_package'
        try:
            requests.post(url, data=json.dumps(package['encrypted']), timeout=0.0001)
        except requests.exceptions.ReadTimeout:
            pass


def main():
    for server_address in settings.SERVERS:
        try:
            url = 'http://' + server_address + '/getServerPublicKey'
            response = requests.get(url, timeout=5)
            online_mixnets[server_address] = response.text
            print("Connected to mixnet: " + server_address)
        except requests.exceptions.ConnectionError:
            print(server_address + " is down.")
            pass
    sched.add_job(send_queued_message, 'interval', seconds=2)
    sched.start()
    socketio.run(app, host='0.0.0.0', port=settings.PORT, debug=settings.DEBUG_MODE)


if __name__ == '__main__':
    main()