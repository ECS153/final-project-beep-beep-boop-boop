# Mixnet Messenger
#### Team Name: BEEP BEEP BOOP BOOP
#### Team Members: Hin Chan, Ryan Chan, Patrick Yieh


The problem we’re solving is the leakage of metadata from messaging systems.
Protecting user privacy is important, especially for people such as whistleblowers 
and medical professionals that send sensitive information. A lot can be inferred by 
simply seeing if two people communicate. Beyond simply encrypting the messages themselves, 
the frequency and recipients of messages amongst other metadata information needs to be 
hidden to guarantee the safety and privacy of messaging.

We know that it is impossible to protect against every type of attack, but our plan is to 
build a messaging system that implements a mixnet to make it a bit more difficult. Our plan 
for the project goes as follows: build a simple messenger, run several servers (or simulate 
servers using our laptops) and write the mixnet protocols, then test the servers to ensure 
we implemented the mixnet properly. The testing will be to make sure messages are delivered 
to the correct users. However, we will also act as the attackers and try to “follow” a 
message through the mixnet to see if we can deduce which users are communicating. 

A success for our software would be that if someone were to follow the messages in our system, 
they would be unable to match the message going into the mixnet with the message going out. 
Our final product should allow users to connect to the chat system and seamlessly communicate 
with each other without any disturbances from the algorithm running in the background. 
