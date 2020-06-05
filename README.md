# Mixnet Messenger

## Get Started

To get started, install the prerequisites by typing the following command:

```bash
pip3 install -r requirements.txt
```

Then, navigate to the `/app` directory to start the servers. You'll need one new terminal for each command / server.


```bash
python3 mixnet.py 5001
```

```bash
python3 mixnet.py 5002
```

```bash
python3 mixnet.py 5003
```

```bash
python3 server.py
```

Note that the mixnets must be started before the frontend server is started.

The app is now available at localhost:5000.



If you chose to not use port 5000 to run the application, update the PORT variable in `app/settings.py`.

```python
PORT = 5000
```



## To Add More Mixnet Servers

You can easily add more mixnet servers by running more instances of:

```bash
python3 mixnet.py (port)
```

After that, you will need to add these servers' ip address to the variable SERVERS in `app/settings.py`. Since this is running locally, the ip address would be '0.0.0.0:(port)'.

```python
PORT = 5000  # this is the port number for the frontend server

...

SERVERS = [
    '0.0.0.0:5001',
    '0.0.0.0:5002',
    '0.0.0.0:5003',
  	# add here
]
```

If you chose not to run the mixnet servers on port 5001, 5002, 5003, you can remove the corresponding line or leave it as is. Our application will ping to the mixnet server to make sure it is online before actually including that server in our mixnet network (which is why the frontend server needs to be run last).



## Code Specifics

### How Public Keys are Shared

When the frontend server is started, a GET request is made to each mixnet server in our list of servers. These requests are caught here:

```python
@app.route('/getServerPublicKey', methods=['GET'])
def get_public_key():
```

This function returns the public key of each server. If there is no response, then the server is assumed to be down and our frontend server won't try to pass messages through there.

<br>

### How Mixnet Servers Handle Messages

Each mixnet server has a POST request handler that accepts incoming packages.

```python
@app.route('/handle_incoming_package', methods=['POST'])
def handle_incoming_packageV2():
```

The packages are converted to JSON, decoded, then reconverted to JSON to be sent off. They are then POST requested to the next server based on the 'recipient' field of the decrypted package. 

<br>

### How the Frontend Server Handles Messages

To avoid having to check if the 'recipient' is a mixnet server or the frontend server, the frontend server has a POST request handler with the same URL but different code.

This handler performs the same decryption, but it also checks if the message was legitimate and not a fake message.

```python
if decrypted['real_package']:
    socketio.emit('message', encode_item(decrypted['encrypted']), room=socket[decrypted['recipient']])
```

The message is only delivered if it was real. Otherwise, it is dropped.



