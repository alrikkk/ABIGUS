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


def parse_container(container: bytes) -> tuple:
    #to check min container length
    if len(container) < HEADER_SIZE + 32:
        raise ValueError("Container is too small")

    #seperating the stored checksum and container data
    stored_checksum = container[-32:]
    container_data = container[:-32]

    calculated_checksum = hashlib.sha256(container_data).digest()

    #this verifies integrity
    if stored_checksum != calculated_checksum:
        raise ValueError("Container Checksum Mismatch")

    header = container_data[:HEADER_SIZE]

    magic, version, metadata_length = struct.unpack(
        HEADER_FORMAT,
        header
    )

    if magic != MAGIC:
        raise ValueError("Invalid ABIGUS container")
    if version != VERSION:
        raise ValueError("Unsupported ABIGUS Version")

    metadata_start = HEADER_SIZE
    metadata_end = metadata_start + metadata_length

    if metadata_end > len(container_data):
        raise ValueError("Metadata extends beyond container data")

    metadata_bytes = container_data[metadata_start:metadata_end]

    try:
        metadata_string = metadata_bytes.decode("utf-8")
        metadata = json.loads(metadata_string)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ValueError("Invalid container metadata")

    if not isinstance(metadata, dict):
        raise ValueError("Metadata must be a dictionary") #or type(metadata) == dict can also do 

    payload = container_data[metadata_end:]

    if "size" not in metadata:
        raise ValueError("Metadata is missing file size")

    if not isinstance(metadata["size"], int) or metadata["size"] < 0:
        raise ValueError("Invalid metadata file size")

    if len(payload) != metadata["size"]:
        raise ValueError("Payload size does not match metadata")

    return metadata, payload

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