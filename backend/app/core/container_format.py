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

    if len(payload) != metadata["size"]:
        raise ValueError("Payload size does not match metadata")
    #building the header
    header = build_header(len(metadata_bytes))
    #combining metadata, header and payload
    container_data = header + metadata_bytes + payload
    #generating SHA - 256 checksum 
    checksum = hashlib.sha256(container_data).digest()

    return container_data + checksum

if __name__ == "__main__":
    test_payload = b"%PDF-1.7 example PDF content"
    sample_metadata = {
        "filename" : "secret.pdf",
        "size" : len(test_payload),
        "format" : "pdf"
    }

    try:
        container = build_container(sample_metadata, test_payload)
        print("Container created:", len(container), "bytes")
        print("First 9 bytes (header): ", container[:9])
        print("Last 32 bytes (checksum): ", container[-32:])
    except ValueError as error:
        print("Container rejected:",error)

    encoded = encode_metadata(sample_metadata)

    print(encoded)
    print(type(encoded))
    print(len(encoded))