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


def encode_metadata(metadata : dict) -> bytes :
    json_string = json.dumps(metadata)
    encoded_data = json_string.encode("utf-8")

    return encoded_data


def build_container(metadata : dict, payload : bytes) -> bytes:
    #encoding the metadata
    metadata_bytes = encode_metadata(metadata)
    #building the header
    header = build_header(len(metadata_bytes))
    #combining metadata, header and payload
    container_data = header + metadata_bytes + payload
    #generating SHA - 256 checksum 
    checksum = hashlib.sha256(container_data).digest()

    return container_data + checksum

if __name__ == "__main__":
    sample_metadata = {
        "filename" : "secret.pdf",
        "size" : 2048,
        "format" : "pdf"
    }

    encoded = encode_metadata(sample_metadata)

    print(encoded)
    print(type(encoded))
    print(len(encoded))