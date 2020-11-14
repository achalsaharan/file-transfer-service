# File Transfer Service
A service that lets servers automatically transfer files to clients. The clients polls the server at regular intervals, the server checks for updates and transfers the files to the clients. <br/></br>
This service can be used to **automatically** send `software updates`, `security patches` or `any type of files` to the clients.
</br>
<p align="center">
  <img src="https://github.com/achalsaharan/file-transfer-service/blob/main/ftc-illustration.png" width="70%" title="hover text">
</p>

## How It Works
This application uses [sockets](https://en.wikipedia.org/wiki/Network_socket) to facilitate communication between the client and the server across the network.

1. The script running on the client side connects to the the server at regular intervals of time.
2. The server checks if there is any file to be transferred corresponding to the client id.
3. If there is a file to be transferred the server sends the file else the connection is closed.

The client and server use custom header and message formats to communicate with each other

### Message Format

#### Client Request Format
```
+---------------------+-------------+
| fixed length header | JSON header |
+---------------------+-------------+
```
* **Fixed length header** is a 2 byte header which is used to tell the size of the JSON header. 
* **The JSON header** can be of any size and contains information like the `client-id`, `request-type` etc in the form of key value pairs.

#### Server Response Format
```
+---------------------+-------------+------------+
| fixed length header | JSON header | file bytes |
+---------------------+-------------+------------+
```
* **Fixed length header** is a 2 byte header which is used to tell the size of the JSON header. 
* **The JSON header** can be of any size and contains information like the `file-name`, `file-size`, `file-hash` etc in the form of key value pairs.
* **File bytes** are the binary bytes of the file. The client receives these bytes and saves them in a file with the `file-name` sent in the fixed length header.

## How To Run
#### Server
The server folder contains the server application, to run the server application. </br>
`python3 fileServer.py`</br>
To configure the `HOSTNAME` and `PORT` go to `serverConfig.py`<\br>

#### Client
The server folder contains the client application, to run the client application. </br>
`python3 fileClient.py`</br>
To configure the `HOSTNAME` and `PORT` go to `clientConfig.py`<\br>

## Team
[Achal Saharan](https://github.com/achalsaharan)</br>
[Achyut Chaudhary](https://github.com/AchyutChaudhary)</br>
[Abhishek Shivaram](https://www.linkedin.com/in/abhishek-shivaram-37889a190)</br>

## Acknowledgements
The article on [Socket Programming in Python](https://realpython.com/python-sockets/) helped in understanding how to use [select](https://docs.python.org/3/library/select.html) with [non-blocking sockets](https://docs.python.org/3.8/howto/sockets.html#non-blocking-sockets) to make a server that can handle multiple connections at a time.<br/>

