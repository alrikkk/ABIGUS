import pytest
import hashlib
from app.core.container_format import build_container, parse_container

def test_container_round_trip():
    payload = b"This is my original file content"
    metadata= {
        "filename": "test.txt",
        "size": len(payload),
        "format": "txt"
    }



    container = build_container(metadata, payload)
    recovered_metadata, recovered_payload = parse_container(container)
    assert recovered_metadata == metadata
    assert recovered_payload == payload

def test_container_rejects_invalid_payload_type():
    metadata = {
        "filename": "test.txt",
        "size": 4,
        "format": "txt"
    }

    with pytest.raises(ValueError, match="Payload must be bytes"):
        build_container(metadata, "ABIG")

def test_parser_rejects_invalid_container_type():
    with pytest.raises(ValueError, match="Container must be bytes"):
        parse_container("ABIG")

def test_parser_rejects_truncated_container():
    with pytest.raises(ValueError, match="Container is too small"):
        parse_container(b"ABIG")

def test_parser_rejects_tampered_container():
    payload = b"Original payload"

    metadata = {
        "filename": "test.txt",
        "size": len(payload),
        "format": "txt"
    }

    container = build_container(metadata, payload)

    #this will create a mutable copy
    tampered_container = bytearray(container)

    #modifies the last byte of the payload
    tampered_container[-33] ^= 1

    with pytest.raises(ValueError, match = "Checksum Mismatch"):
        parse_container(bytes(tampered_container))

def test_parser_rejects_invalid_magic():
    payload = b"Original Payload"

    metadata = {
        "filename": "test.txt",
        "size": len(payload),
        "format": "txt"
    }

    container = bytearray(build_container(metadata, payload))

    #replacing the 4-byte magic identifier
    container[:4] = b"NOPE"

    #Recalculating the checksum so that the integrity verification passes
    container_data = bytes(container[:-32])
    new_checksum = hashlib.sha256(container_data).digest()
    container[-32:] = new_checksum

    with pytest.raises(ValueError, match = "Invalid ABIGUS container"):
        parse_container(bytes(container))

def test_build_container_rejects_path_transversal():
    payload = b"test"
    metadata = {
        "filename": "../../secret.pdf",
        "size": len(payload),
        "format": "pdf"
    }

    with pytest.raises(ValueError, match="directory path"):
        build_container(metadata, payload)

def test_build_container_rejects_empty_filename():
    payload = b"test"
    metadata = {
        "filename": "   ", #this is to test that strip func in the other main file
        "size": len(payload), #🤣
        "format": "txt"
    }

    with pytest.raises(ValueError, match = "Invalid filename"):
        build_container(metadata, payload)

def test_build_container_rejects_absolute_path():
    payload = b"test"
    metadata = {
        "filename": "/Users/someone/secret.pdf",
        "size": len(payload),
        "format": "pdf"
    }

    with pytest.raises(ValueError, match = "directory path"):
        build_container(metadata, payload)

def test_build_container_rejects_windows_path():
    payload = b"test"

    metadata = {
        "filename": "C:\\Users\\someone\\secret.pdf",
        "size": len(payload),
        "format": "pdf"
    }

    with pytest.raises(ValueError, match="directory path"):
        build_container(metadata, payload)
        
def test_build_container_rejects_windows_drive_relative_path():
    payload = b"test"
    metadata = {
        "filename": "C:secret.pdf",
        "size": len(payload),
        "format": "pdf"
    }

    with pytest.raises(ValueError, match="directory path"):
        build_container(metadata, payload)

@pytest.mark.parametrize(
    "filename",
    [
        "report.pdf",
        "my project.zip",
        "résumé.txt",
        "image_2026.png",
    ]
)
def test_build_container_accepts_valid_filenames(filename):
    payload = b"test"
    metadata = {
        "filename": filename,
        "size": len(payload),
        "format": "test"
    }

    container = build_container(metadata, payload)
    recovered_metadata, recovered_payload = parse_container(container)
    assert recovered_metadata["filename"] == filename
    assert recovered_payload == payload

@pytest.mark.parametrize(
    "missing_field",
    ["filename", "size", "format"]
)
def test_build_container_rejects_missing_metadata_fields(missing_field):
    payload =b"test"
    metadata = {
        "filename": "test.txt",
        "size": len(payload),
        "format": "txt"
    }
    metadata.pop(missing_field)
    with pytest.raises(ValueError, match=f"Metadata is missing: {missing_field}"):
        build_container(metadata, payload)

def test_build_container_rejects_boolean_size():
    payload =b"x"

    metadata = {
        "filename": "test.txt",
        "size": True,
        "format": "txt"
    }

    with pytest.raises(ValueError, match="Invalid metadata file size"):
        build_container(metadata, payload)

@pytest.mark.parametrize(
    ("field", "invalid_value", "expected_error"),
    [
        ("filename", None, "Invalid filename"),
        ("filename", 123, "Invalid filename"),
        ("format", None, "invalid file format"),
        ("format", 123, "invalid file format"),
    ]
)
def test_build_container_rejects_invalid_metadata_types(field, invalid_value, expected_error):
    payload = b"test"
    metadata = {
        "filename": "test.txt",
        "size": len(payload),
        "format": "txt"
    }
    field

    metadata[field] = invalid_value
    with pytest.raises(ValueError, match = expected_error):
        build_container(metadata, payload)