import socket
from clientConfig import HOST, PORT, CLIENT_ID
import struct
import json
import io

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
content = sock.recv(content_length)
content = _json_decode(content, "utf-8")
print(content)

sock.close()
