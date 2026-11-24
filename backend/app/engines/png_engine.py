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

def decode_from_png(png_data: bytes) -> bytes:
    if not isinstance(png_data, bytes):
        raise TypeError("PNG data must be bytes")
    try:
        #to open PNG from memory
        image = Image.open(io.BytesIO(png_data))

        #to only accept genuine PNG's
        if image.format != "PNG":
            raise ValueError("Invalid image format")

        image.load()

        #encoder - RGB Images
        if image.mode != "RGB":
            raise ValueError("Invalid PNG colour mode")

        #extracting all pixel data
        raw_data = image.tobytes()
    
    except (Image.UnidentifiedImageError, OSError) as error:
        raise ValueError("Invalid or currupted PNG") from error

    #to check if data is lesser than 8 bytes 
    if len(raw_data) < 8:
        raise ValueError("PNG data is too small")

    #Recovering th OG Container length
    container_length = struct.unpack(">Q", raw_data[:8])[0]

    #to make sure the declared length fits inside the img 
    if container_length == 0 or container_length > len(raw_data) - 8:
        raise ValueError("Invalid container length")
    
    #extracting only the og container, excluding the padding 
    container = raw_data[8:8 + container_length]

    return container