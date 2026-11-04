import json
import struct
import hashlib


MAGIC = b"ABIG"
VERSION = 1
HEADER_FORMAT = ">4sBI"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

print(HEADER_SIZE)

def build_header(metadata_length: int) -> bytes:
    return struct.pack(
        HEADER_FORMAT,
        MAGIC,
        VERSION,
        metadata_length
     )

if __name__ == "__main__":
    header = build_header(256)
    print(header)
    print(len(header))  #to print its length