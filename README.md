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

### Our Encryption

Our encryption follows the documentation [here](https://pycryptodome.readthedocs.io/en/latest/src/examples.html#generate-public-key-and-private-key) for RSA encryption.

Our encrypt function is
```python
def encrypt(data, public_key):
```
The sesssion key is encrypted with the public RSA key, and the data is encrypted with the AES session key.

In the decrypt function,
```python
def decrypt(encoded_data, private_key):
```
The session key is decrypted with the private RSA key, and the data is decrypted with the AES session key.

One important factor to note is that in order to encrypt multiple times, the package must be converted to base 64. This is handled with

```python
def decode_array(array):
def encode_array(array):
def decode_item(byte):
def encode_item(byte):
```

in RSA_script.py. The reason why there are two variation of encode/decode is because Web Crypto (crypto library we used on JavaScript) returns bytes upon encrypting whereas PyCryptodome returns an array of bytes.

<br>

### How Public Keys are Shared

When the frontend server is started, a GET request is made to each mixnet server in our list of servers. These requests are caught here:

```python
@app.route('/getServerPublicKey', methods=['GET'])
def get_public_key():
```

This function returns the public key of each server. If there is no response, then the server is assumed to be down and our frontend server won't try to pass messages through there. The mapping of the server address and public key are then stored and distrubuted when a user connect to the application socket.

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

<br>

### How Noise is Added

When each server is started, a scheduler is also started. 

```python
sched.add_job(send_queued_message, 'interval', seconds=2)
sched.start()

def send_queued_message():
    generate_noise()
    random.shuffle(post_msg_queue)
```

When the 2s interval passes, fake messages are added to our message queue, which are then shuffled and sent out all at once.

<br>


#### How Fake Messages are Created

For each message queue, a random number of fake messages are created, ranging from 1-2 times that of real messages. We encrypt them the same way as real messages but with the parameters as follows.

```python
package = decode_array(encrypt(json.dumps({
            "encrypted": decode_array(encrypt("beepbeepboopboop".encode("utf-8"), key.getPublicKey())),
            "recipient": "",
            "real_package": False
        }).encode("utf-8"), key.getPublicKey()))
```

The frontend server will check for the real_package boolean and drop fake messages.

<br>








