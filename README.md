# Mixnet Messenger

## Get Started

Our project is a flask app, so the first step is to pip3 install the requirements from the root directory:

```bash
pip3 install -r requirements.txt
```

Then, navigate to the /app directory to start the servers. You'll need one new terminal for each command/server


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
