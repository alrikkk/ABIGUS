"""the reason that i am taking soo long to do this is cause i forgot all about binary data and 
have to learn everything one by one and i also have college work to look at , anyways i will try to 
complete this ASAP, thanks 😊"""

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

def validate_metadata(metadata: dict) -> None:
    if not isinstance(metadata, dict):
        raise ValueError("Metadata must be a dictionary")

    #to check the required fields 
    required_fields = ["filename", "size", "format"]

    for field in required_fields:
        if field not in metadata:
            raise ValueError(f"Metadata is missing: {field}")

    #validating file name
    if not isinstance(metadata["filename"], str) or not metadata["filename"].strip():
        raise ValueError("Invalid filename")

    #validating file size
    if type(metadata["size"]) is not int or metadata["size"] < 0:
        raise ValueError("Invalid metadata file size")

    #validating file format
    if not isinstance(metadata["format"], str) or not metadata["format"].strip():
        raise ValueError("invalid file format")


def build_container(metadata: dict, payload: bytes) -> bytes:
    validate_metadata(metadata)

    # Encoding the metadata
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

    validate_metadata(metadata)
    payload = container_data[metadata_end:]

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

        #trying to tamper
        tampered_container = bytearray(container)

        #changing one byte in the payload
        tampered_container[HEADER_SIZE + len(encode_metadata(sample_metadata))] ^= 1

        try:
            parse_container(bytes(tampered_container))
            print("Tampering went undetected!")
        except ValueError as error:
            print("Tampering detected: ", error)
        print("Container created:", len(container), "bytes")
        print("First 9 bytes (header): ", container[:9])
        print("Last 32 bytes (checksum): ", container[-32:])

        #to test container recovery
        recovered_metadata, recovered_payload = parse_container(container)
        print("Recovered meatdata: ", recovered_metadata)
        print("Recovered payload: ", recovered_payload)

        #to compare the original and recovered data
        print("Payload matches: ", recovered_payload == test_payload)
        print("Metadata matches: ", recovered_metadata == sample_metadata)
    except ValueError as error:
        print("Container rejected:",error)

    encoded = encode_metadata(sample_metadata)

    print(encoded)
    print(type(encoded))
    print(len(encoded))