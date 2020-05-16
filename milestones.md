
# Milestone 2

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
