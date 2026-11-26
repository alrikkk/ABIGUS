from pathlib import Path
from app.core.container_format import build_container
from app.engines.png_engine import encode_to_png
from app.core.container_format import build_container, parse_container
from app.engines.png_engine import encode_to_png, decode_from_png

def store_file_as_png(
    source_path: str,
    output_path: str
) -> None:

    source = Path(source_path)
    output = Path(output_path)

    # Read the original file
    original_data = source.read_bytes()

    # Create metadata
    metadata = {
        "filename": source.name,
        "size": len(original_data),
        "format": source.suffix.lstrip(".").lower() or "bin"
    }

    # Build the ABIGUS container
    container = build_container(metadata, original_data)

    # Encode the container into PNG
    png_data = encode_to_png(container)

    # Save the PNG
    output.write_bytes(png_data)