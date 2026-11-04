import json
import struct
import hashlib


MAGIC = b"ABIG"
version = 1
HEADER_FORMAT = ">4sBI"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

print(HEADER_SIZE)