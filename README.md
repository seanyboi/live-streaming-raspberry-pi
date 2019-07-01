# Why Stream Frames?
Streaming frames allows us to do expensive computations on a server that 
our client machine may not be able to do. Computations such as neural 
networks, Machines such as Raspberry Pi's.

# Message Passing
Message passing allows one process to communicate with other processes 
using a message broker. In order to communicate with other processes a 
request must be sent to the message broker. The message broker than 
sends messages to other processes asking "Hey look at this?". It then 
packages all the responses and sends it back to the original process.

# ZMQ
A high performance asynchronous message passing library.
Advantages: High throughout (lots of new frames)  and low latency 
applications (frames distrubuted to all nodes on system as soon as)

# Client / Server Relationship
Client reads frame webcam and send frame to server
Server accepts frames, acknowledge receipt, process frames, show output 
live streams


