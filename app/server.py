
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, close_room, disconnect
import json
import RSA_script
import settings


# https://stackoverflow.com/questions/45918818/how-to-send-message-from-server-to-client-using-flask-socket-io

# refer to https://flask-socketio.readthedocs.io/en/latest/
# for flask socketio


app = Flask(__name__)
app.config['SECRET KEY'] = settings.APP_SECRET_KEY
socketio = SocketIO(app, ping_interval=settings.PING_INTERVAL, ping_timeout=settings.PING_TIMEOUT)
client = {}
socket = {}  # username as key, sid as value
socket_inv = {}  # sid as value, username as key


@app.route('/')
def sessions():
    return render_template('website.html')


@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('public key', {"public_key": RSA_script.Keys.getPublicKey().export_key(settings.KEY_ENCODING_EXTENSION)})


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
        emit('disconnect', data, room=socket[data['username']])  # to let client know, actual disconnect will happen from timeout
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
    emit('message', data['encrypted'], room=socket[data['recipient']])

    # FIXME: when we do mixnet
    # onion layer should goes as follows: ( ) indicates client encryption, < > indicates server encryption
    # < < < < < ( message, sender ), recipient, this server >, mixnet server 2 >, mixnet server 1 >, this server >
    # client should be given list of all the mixnet server IP and public key and create this route
    #
    # http request to recipient server, then each mixnet server peel off a layer
    # when it comes back to this server, emit('message', data, room=socket[data['recipient']])


def main():
    # ENCRYPTION SAMPLE
    # data = "I am a potato who is eating potato from a potato plant in a potato farm."
    # encrypted_data = RSA_script.encrypt(data.encode("utf-8"), RSA_script.Keys.getPublicKey())
    # decrypted_data = RSA_script.decrypt(encrypted_data)
    #
    # print("************Encryption Test***************")
    # print("Original: ", data)
    # print("***************************")
    # print("Encrypted: ", encrypted_data)
    # print("***************************")
    # print("Decrypted: ", decrypted_data)
    # print("***************************")

    socketio.run(app, host='0.0.0.0',  port=settings.PORT, debug=settings.DEBUG_MODE, ssl_context=('cert.pem', 'key.pem'))


if __name__ == '__main__':
    main()
