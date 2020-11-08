import sys
import selectors
import struct
import json
import io
import socket

from databaseConnection import Database

# Check fixed len header and json header to find client_id
# Then check if an update is present

# incoming request
# fixed len header (2 bytes) | JSON Header | data(if necessary)
# incomming JSON Header format
# {
#     "content-type",
#     "client_id",
#     "content-length"
# }

# outgoing request
# fixed len header (2 bytes) | JSON Header | file (if found)
# outgoing JSON header format
# {
#     "byteorder": sys.byteorder,
#     "content-type": content_type,
#     "content-encoding": content_encoding,
#     "content-length": len(content_bytes),
#     "file-name",
#     "extension",
#     "md-5-hash",

# }


class ResponseHeader:
    def __init__(self, byteorder, content_type, content_encoding, content_length, filename):
        self.byteorder = byteorder
        self.content_type = content_type
        self.content_encoding = content_encoding
        self.content_length = content_length
        self.filename = filename

    def createHeader(self):
        db = Database()
        md_5_hash = db.findFileHash(self.filename)
        extension = self.filename.split('.')[1]
        jsonHeader = {
            "byteorder": sys.byteorder,
            "content-type": self.content_type,
            "content-encoding": self.content_encoding,
            "content-length": self.content_length,
            "file-name": self.filename,
            "extension": extension,
            "md-5-hash": md_5_hash
        }
        return jsonHeader


class Message:
    def __init__(self, selector, sock, addr):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self.jsonheader = None
        self.request = None
        self.response_created = None
        self.filename = None
        self._recv_buffer = b""
        self._send_buffer = b""
        self._jsonheader_len = None
        self.db = Database()

    def _set_selector_events_mask(self, mode):
        # Set selector to listen for events: mode is 'r', 'w', or 'rw'.
        if mode == "r":
            events = selectors.EVENT_READ
        elif mode == "w":
            events = selectors.EVENT_WRITE
        elif mode == "rw":
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            raise ValueError(f"Invalid events mask mode {repr(mode)}.")

        # Modifying selector event mask
        self.selector.modify(self.sock, events, data=self)

    def _read(self):
        try:
            data = self.sock.recv(4096)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self._recv_buffer += data
            else:
                raise RuntimeError("Peer closed.")

    def _write(self):
        if self._send_buffer:
            print(f"senfing {repr(self._send_buffer)} to {self.addr}")

            try:
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]
                # Close when the buffer is drained. The response has been sent.
                if sent and not self._send_buffer:
                    self.close()

    # Decodes bytes into JSON
    def _json_decode(self, json_bytes, encoding):
        tiow = io.TextIOWrapper(
            io.BytesIO(json_bytes), encoding=encoding, newline=""
        )
        obj = json.load(tiow)
        tiow.close()
        return obj

    # Encode JSON into bytes
    def _json_encode(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def _create_response_json_content(self):

        # we are creating the actual response here
        # neither the json header nor the fixed length header

        # looks like this is not even the actual response

        if self.filename == 0:
            content = {
                "update": "False",
                "filename": "none"
            }
        else:
            content = {
                "update": "True",
                "filename": self.filename
            }

        content_encoding = "utf-8"
        response = {
            "content_bytes": self._json_encode(content, content_encoding),
            "content_type": "text/json",
            "content_encoding": content_encoding,
        }
        return response

    def _create_response_binary_content(self):
        response = {
            "content_bytes": b"First 10 bytes of request: ",
            # + self.request[:10],
            "content_type": "binary/custom-server-binary-type",
            "content_encoding": "binary",
        }
        return response

    def _create_message(
        self, *, content_bytes, content_type, content_encoding
    ):
        # jsonheader = {
        #     "byteorder": sys.byteorder,
        #     "content-type": content_type,
        #     "content-encoding": content_encoding,
        #     "content-length": len(content_bytes),
        # }
        header = ResponseHeader(
            sys.byteorder, 'text/json', content_encoding, len(content_bytes), 'file1.txt')
        jsonheader = header.createHeader()

        jsonheader_bytes = self._json_encode(jsonheader, "utf-8")
        message_hdr = struct.pack(">H", len(jsonheader_bytes))
        message = message_hdr + jsonheader_bytes + content_bytes
        return message

    def process_events(self, mask):
        if selectors.EVENT_READ & mask:
            self.read()
        if selectors.EVENT_WRITE & mask:
            self.write()

    def read(self):

        self._read()

        if self._jsonheader_len is None:
            self.process_protoheader()

        if self._jsonheader_len is not None:
            if self.jsonheader is None:
                self.process_jsonheader()

        if self.jsonheader:
            self.process_request()

    def write(self):
        if self.request:
            if not self.response_created:
                self.create_response()

        self._write()

    def process_protoheader(self):
        hdrlen = 2

        if len(self._recv_buffer) >= hdrlen:
            self._jsonheader_len = struct.unpack(
                ">H", self._recv_buffer[:hdrlen])[0]

            self._recv_buffer = self._recv_buffer[hdrlen:]

    def process_jsonheader(self):
        hdrlen = self._jsonheader_len

        if len(self._recv_buffer) >= hdrlen:
            self.jsonheader = self._json_decode(
                self._recv_buffer[:hdrlen], "utf-8")

            self._recv_buffer = self._recv_buffer[hdrlen:]

            # Checking if the header has all fields
            for reqhdr in (
                "content-type",
                "client_id",
                "content-length"
            ):
                if reqhdr not in self.jsonheader:
                    raise ValueError(f'Missing required header "{reqhdr}".')

    def process_request(self):
        # At this point we have the json header
        # We need to check for updates and respond
        client_no = self.jsonheader["client_id"]
        filename = self.db.checkUpdate(client_no)

        if filename == 0:
            self.filename = 0
            print('no file to send')
        else:
            self.filename = filename
            print(f'sending {self.filename} to {self.addr}')

        # Set selector to listen for write events, we're done reading.
        self.request = 1
        print('done reading....')
        print(self.jsonheader)
        self._set_selector_events_mask("w")

    def create_response(self):
        if self.jsonheader["content-type"] == "text/json":
            response = self._create_response_json_content()
        else:
            # Binary content
            response = self._create_response_binary_content()

        message = self._create_message(**response)
        self.response_created = True
        self._send_buffer += message

    def close(self):
        print("closing connection to", self.addr)
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            print(
                "error: selector.unregister() exception for",
                f"{self.addr}: {repr(e)}",
            )

        try:
            self.sock.close()
        except OSError as e:
            print(
                "error: socket.close() exception for",
                f"{self.addr}: {repr(e)}",
            )
        finally:
            # Delete reference to socket object for garbage collection
            self.sock = None