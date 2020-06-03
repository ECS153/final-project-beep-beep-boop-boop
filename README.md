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









