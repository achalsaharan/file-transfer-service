import socket
from clientConfig import HOST, PORT, CLIENT_ID
import struct
import json
import io
import tqdm
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
sock.connect((HOST, PORT))


def _json_encode(obj, encoding):
    return json.dumps(obj, ensure_ascii=False).encode(encoding)


def _json_decode(json_bytes, encoding):
    tiow = io.TextIOWrapper(
        io.BytesIO(json_bytes), encoding=encoding, newline=""
    )
    obj = json.load(tiow)
    tiow.close()
    return obj


json_header = {
    "content-type": "text/json",
    "client_id": 6,
    "content-length": 0
}

# encode json header
json_header_encoded = _json_encode(json_header, "utf-8")

# creating message
message_hdr = struct.pack(">H", len(json_header_encoded))
message = message_hdr + json_header_encoded
sock.send(message)

# recieving the fixed len header
fixed_hdr = sock.recv(2)
json_header_len = struct.unpack(">H", fixed_hdr)[0]

# recieving the json header
res_json_header = sock.recv(json_header_len)
json_header = _json_decode(res_json_header, "utf-8")
print(json_header)

# reciving the content
content_length = json_header['content-length']
if content_length == 0:
    print("***No updates from server***")
else:
    content_length = int(content_length)
    content = sock.recv(content_length)
    print(len(content))
    print(content_length)
    # content = _json_decode(content, "utf-8")
    filename = "client_executable.exe"
    with open(filename, "wb") as f:
        f.write(content)
    # progress = tqdm.tqdm(range(content_length), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    # with open(filename, "wb") as f:
    #     for _ in progress:
    #         # read 1024 bytes from the socket (receive)
    #         # bytes_read = client_socket.recv(BUFFER_SIZE)
    #         bytes_read = content
    #         if not bytes_read:    
    #             # nothing is received
    #             # file transmitting is done
    #             break
    #         # write to the file the bytes we just received
    #         f.write(bytes_read)
    #         # update the progress bar
    #         progress.update(len(bytes_read))
    # print(content)

sock.close()
