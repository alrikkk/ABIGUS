import io
import pytest
from PIL import Image
import struct
from app.engines.png_engine import encode_to_png, decode_from_png
from app.core.container_format import build_container, parse_container

#png helper
def create_test_png(mode, size, raw_data):
    image = Image.frombytes(mode, size, raw_data)
    output = io.BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()

def test_png_round_trip():
    original_data = b"Hello ABIGUS! This is our first PNG storage test."

    #encoding the og bytes into the png
    png_data = encode_to_png(original_data)

    #decoding the png back into bytes
    decoded_data = decode_from_png(png_data)

    assert decoded_data == original_data

@pytest.mark.parametrize(
    "original_data",
    [
        b"\x00\x01\x02\x03\x04\x05",
        bytes(range(256)),
        b"%PDF-1.7\x00\xff\xfe binary PDF data",
        b"PK\x03\x04\x00\x00\xff\xfe ZIP-like data",
    ],
)

def test_png_binary_round_trip(original_data):
    png_data = encode_to_png(original_data)
    decoded_data = decode_from_png(png_data)

    assert decoded_data == original_data

def test_encode_rejects_non_bytes():
    with pytest.raises(TypeError, match="Container must be bytes"):
        encode_to_png("hello")

def test_encode_rejects_empty_data():
    with pytest.raises(ValueError, match="Container cannot be empty"):
        encode_to_png(b"")

def test_decode_rejects_non_bytes():
    with pytest.raises(TypeError, match="PNG data must be bytes"):
        decode_from_png("non bytes")

def test_decode_rejects_invalid_png():
    with pytest.raises(ValueError, match="Invalid or currupted PNG"):
        decode_from_png(b"not a png")

#tests (three below)
def test_decode_rejects_non_rgb_png():
    png_data = create_test_png(
        "RGBA",
        (1, 1),
        b"\x00\x00\x00\xff"
    )

    with pytest.raises(ValueError, match="Invalid PNG colour mode"):
        decode_from_png(png_data)

def test_decode_rejects_png_too_small():
    png_data = create_test_png(
        "RGB",
        (1, 2),
        b"\x00" * 6
    )
    with pytest.raises(ValueError, match="PNG data is too small"):
        decode_from_png(png_data)

def test_decode_rejects_invalid_container_length():
    raw_data = struct.pack(">Q", 999) + b"\x00\x01\x02\x03"
    png_data = create_test_png(
        "RGB",
        (4, 1),
        raw_data
    )

    with pytest.raises(ValueError, match="Invalid container length"):
        decode_from_png(png_data)


def test_container_png_round_trip():
    original_payload = b"%PDF-1.7\x00\xff\xfe ABIGUS integration test"

    metadata = {
        "filename": "report.pdf",
        "size": len(original_payload),
        "format": "pdf"
    }

    #building the container
    container = build_container(metadata, original_payload)

    #storing the container inside a PNG
    png_data = encode_to_png(container)

    #recovering the og container
    recovered_container = decode_from_png(png_data)

    assert recovered_container == container

    #extracting the og data from the container
    recovered_metadata, recovered_payload = parse_container(recovered_container)

    assert recovered_metadata == metadata
    assert recovered_payload == original_payload