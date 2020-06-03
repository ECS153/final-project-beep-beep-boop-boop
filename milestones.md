# Final Presentation
### 6/3/2020 Presentation Day
Video [here](https://drive.google.com/file/d/1_kyEAb9YVNagvDoS0vjFa4lNSCHDLQNd/view?usp=sharing)



# Milestone 3
### 5/26/2020 Meeting:
__General updates:__
* Hin
    * Messenger, client and server
    * Design doc [here](https://drive.google.com/open?id=10iXIhPNr6L_bwHTY6exelX9roOYps0DCxlVlcjvgl6Q)
    * Action item: help Ryan with encryption
* Ryan
    * Importing / exporting encryption keys (Client)
    * Design doc: [here](https://drive.google.com/open?id=1R9tIxG5AqJVSUjScXPtiAXdhUqcRYamuthF7OYNpJHs)
    * Action item: Import key generated on pycryptodome on client’s end
* Patrick 
    * Host server, GET request to retrieve server public keys (Mixnet)
    * Design doc [here](https://docs.google.com/document/d/18s74NmGxdNouq81UD24lhhx95ZskYEFLPxZUpY-tmvw/edit?usp=sharing)
    * Action item: Finalize data forwarding

__Agenda:__
* Troubleshoot bugs
* Film video for milestone 3 [Here](https://drive.google.com/file/d/1OyJe8NNEQ9vy0gqHC2-GeHYXoPxmRir4/view?usp=sharing)

__Notes:__
* Ask Sam if it would be a better idea to ditch pyCryptodome and instead make a separate JS script on the server so server keys are generated through Web Crypto as well. There shouldn’t be any more conflict that way. We spent 4 days on this already.



# Milestone 2
### 5/19/2020 Meeting
__General updates:__
* Hin
    * Action item: Set up “sender” server
* Ryan
    * Action item: Figure out how to store keys on client
* Patrick 
    * Action item: Figure out how to host and connect servers

__Agenda:__
* Film video for milestone 2. [Here](https://drive.google.com/file/d/11y0bv1eSWeUGkLgmSXikXMQiJ87neDG-/view?usp=sharing)

__Notes:__ 
* Deploy servers
    * Last server in chain will be the “sender” server
    * Via Digital Ocean or PythonAnywhere
* Client to send message to server
    * Request server’s public key (done) and recipient's public key
    * Encrypt using recipient’s public key
    * Attach recipient, encrypt using the server public key and send it off to the server
* Inter-server communication
    * Set up sockets between servers



### 5/16/2020 Meeting
__General updates:__
* Hin
    * Action item: Encrypt / decrypt message testing on the server
* Ryan
    * Action item: Generate and store RSA public private key on client
* Patrick 
    * Action item: Figure out why the webpage is not receiving the public key from the server (localhost)
* Everyone
    * Make proposal video tomorrow

__Agenda:__
* How to store user private key if we’re doing a webapp
* Terminal or webapp? Sticking with webapp for now.

__Notes:__
* Use [API](https://www.w3.org/TR/WebCryptoAPI/) to store key pairs. Keep going with webapp.
* RSA keys in PEM extension
* Public key as user id (server have a database that maps public key to user name)
* Key pairs are stored on the client (perhaps a folder architecture like this:)
  * User1
    * Public key
    * Private key
    * Name.txt
* Server sends out list of people online every ten seconds (flask supports this, socketio.emit(..))


# Milestone 1

### 5/12/2020 Meeting
__General updates:__
* Everyone
   * Made proposal video [here](https://drive.google.com/file/d/1BX0ShXLLu6uYyixAmfiosh9aUVE2xdBV/view?usp=sharing)

---

### 5/11/2020 Meeting
__General updates:__
* Hin
    * Action item: Implement simple messaging system (demo)
* Ryan
    * Action item: Figure out how to implement mixnet
* Patrick 
    * Action item: Figure out how to host our server
* Everyone
    * Make proposal video tomorrow

__Agenda:__
* How to host the application
    * Ask if we need to host it live.
* What language to use
    * Flask for built in socket handling
* Make the messenger system
    * Try and avoid dead drop
