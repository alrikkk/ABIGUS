import io
import math
import struct

from PIL import Image

IMAGE_WIDTH = 256

def encode_to_png(container: bytes) -> bytes:
    if not isinstance(container, bytes):
        raise TypeError("Container must be bytes")

    if not container:
        raise ValueError("Container cannot be empty")

    #to store the original container length as a 8-byte integer.
    length_header = struct.pack(">Q", len(container))

    #combining the length header and container
    raw_data = length_header + container

    #each RGB pixel will store 3 bytes
    pixel_count = math.ceil(len(raw_data) / 3)
    height = math.ceil(pixel_count / IMAGE_WIDTH)

    #PNG dimension to be completly filled with pixle data
    padding_length = IMAGE_WIDTH * height * 3 - len(raw_data)
    raw_data += b"\x00" * padding_length

    #converting the bytes into an RGB image
    image = Image.frombytes(
        "RGB",
        (IMAGE_WIDTH, height),
        raw_data
    )

    #save the image into the memory as a genuine PNG ;)
    output = io.BytesIO()
    image.save(output, format="PNG")

    return output.getvalue()