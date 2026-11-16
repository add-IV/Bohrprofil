"""Image export: PNG via Pillow, PDF via a minimal hand-written PDF writer.

The PDF writer embeds the rendered image as a single JPEG on an A4 page at
its true physical size (300 DPI), avoiding a heavyweight PDF dependency.
"""

import io

from PIL import Image

from .utils import DPI

A4_WIDTH_PT, A4_HEIGHT_PT = 595.28, 841.89
PAGE_MARGIN_PT = 40


def image_to_pdf_bytes(image: Image.Image) -> bytes:
    jpeg_buf = io.BytesIO()
    image.convert("RGB").save(jpeg_buf, format="JPEG", quality=95)
    jpeg_bytes = jpeg_buf.getvalue()

    w_pt = image.width * 72 / DPI
    h_pt = image.height * 72 / DPI
    pw, ph, margin = A4_WIDTH_PT, A4_HEIGHT_PT, PAGE_MARGIN_PT

    # Place the image at the top-left of the page, scaled to its physical size.
    content = (
        f"q {w_pt:.2f} 0 0 {h_pt:.2f} {margin:.2f} {ph - h_pt - margin:.2f} cm /Im0 Do Q"
    ).encode()

    objs = {
        1: (
            b"<</Type /XObject /Subtype /Image"
            b" /Width " + str(image.width).encode()
            + b" /Height " + str(image.height).encode()
            + b" /ColorSpace /DeviceRGB /BitsPerComponent 8"
            b" /Filter /DCTDecode"
            b" /Length " + str(len(jpeg_bytes)).encode()
            + b">>\nstream\n" + jpeg_bytes + b"\nendstream"
        ),
        2: b"<</Length " + str(len(content)).encode() + b">>\nstream\n" + content + b"\nendstream",
        3: (
            f"<</Type /Page /Parent 4 0 R /MediaBox [0 0 {pw} {ph}] /Contents 2 0 R"
            f" /Resources <</XObject <</Im0 1 0 R>>>>>>"
        ).encode(),
        4: b"<</Type /Pages /Kids [3 0 R] /Count 1>>",
        5: b"<</Type /Catalog /Pages 4 0 R>>",
    }

    out = io.BytesIO()
    out.write(b"%PDF-1.4\n")
    offsets = {}
    for n, data in objs.items():
        offsets[n] = out.tell()
        out.write(f"{n} 0 obj\n".encode() + data + b"\nendobj\n")

    xref_pos = out.tell()
    out.write(b"xref\n0 " + str(len(objs) + 1).encode() + b"\n")
    out.write(b"0000000000 65535 f \n")
    for n in range(1, len(objs) + 1):
        out.write(f"{offsets[n]:010d} 00000 n \n".encode())
    out.write(
        f"trailer\n<</Size {len(objs) + 1} /Root 5 0 R>>\nstartxref\n{xref_pos}\n%%EOF\n".encode()
    )
    return out.getvalue()


def save_image(image: Image.Image, filename: str) -> None:
    """Save as PDF if the filename ends in ``.pdf``, otherwise let Pillow pick the format."""
    if filename.lower().endswith(".pdf"):
        with open(filename, "wb") as f:
            f.write(image_to_pdf_bytes(image))
    else:
        image.save(filename)
