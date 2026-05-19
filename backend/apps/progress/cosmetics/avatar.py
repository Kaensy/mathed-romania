"""Avatar upload validation + normalization.

Every accepted avatar passes through this module before being persisted:
the byte stream is validated by *opening it with Pillow* (never trusting
the Content-Type header), guarded against decompression-bomb dimensions
and against an oversized file, then normalised — EXIF orientation
applied, center-cropped to a square, resized to a bounded side, stripped
of metadata, and re-encoded into one consistent format. The output is a
byte blob + extension the service layer writes under a generated name.

Pure module: no Django/model imports. The view passes us a Django
UploadedFile (or any file-like object exposing `.size`, `.seek`, and a
readable stream) and we return bytes — storage and the avatar_source
field flip live in service.upload_avatar.
"""
import io

from PIL import Image, ImageOps, UnidentifiedImageError

# Reject the upload at the request edge before touching Pillow — protects
# the worker from spending CPU on obviously-too-large blobs.
MAX_INPUT_BYTES = 5 * 1024 * 1024  # 5 MB

# Cap on input *pixel count* — the decompression-bomb knob. PIL's default
# is ~89 million; ours is 50 million (≈ 7000×7000), generous for any real
# camera photo and tight enough that a malformed header asking for 100k×
# 100k will never reach the decoder. Checked explicitly so we don't have
# to mutate the module-global `Image.MAX_IMAGE_PIXELS`.
MAX_INPUT_PIXELS = 50_000_000

# Output is a 256×256 JPEG. Square so the frontend never has to crop;
# JPEG so animated GIFs / multi-frame TIFFs collapse to a single frame
# on re-encode (one consistent format on the wire).
OUTPUT_SIDE = 256
OUTPUT_FORMAT = "JPEG"
OUTPUT_EXT = "jpg"
JPEG_QUALITY = 90


class InvalidAvatarUpload(ValueError):
    """Raised when an avatar upload is rejected. Carries a Romanian
    message the view surfaces verbatim in the 400 response."""

    def __init__(self, message_ro: str):
        super().__init__(message_ro)
        self.message_ro = message_ro


def normalize_avatar_upload(uploaded) -> tuple[bytes, str]:
    """Validate `uploaded` and return its normalised (`bytes`, `ext`).

    Validation gates, in order:
    1. Reported size ≤ MAX_INPUT_BYTES (cheapest reject).
    2. Pillow can open + verify the stream (catches malformed / non-image
       files; never trusts Content-Type).
    3. Decoded dimensions × dimensions ≤ MAX_INPUT_PIXELS.

    Normalisation pass (in order, so each step composes on the last):
    1. EXIF orientation transposed (also strips the EXIF block).
    2. Center-cropped to a square at OUTPUT_SIDE.
    3. Converted to RGB (drops alpha; JPEG doesn't carry one).
    4. Saved as JPEG into a fresh buffer with no `info` dict — this is
       what removes the remaining metadata (ICC profile, GPS, etc).
    Raises InvalidAvatarUpload on any failure; the view translates that
    to a 400.
    """
    size = getattr(uploaded, "size", None)
    if size is None or size > MAX_INPUT_BYTES:
        raise InvalidAvatarUpload(
            "Imaginea este prea mare. Maxim 5 MB."
        )

    # Pass 1: verify. `Image.verify()` only checks the header / file
    # structure — cheap, doesn't decode pixels. Consumes the stream.
    uploaded.seek(0)
    try:
        with Image.open(uploaded) as probe:
            probe.verify()
    except (UnidentifiedImageError, OSError, ValueError):
        # `from None` — the original Pillow exception is implementation
        # detail; the user-facing 400 message is the whole point.
        raise InvalidAvatarUpload(
            "Fișierul nu este o imagine validă."
        ) from None

    # Pass 2: open + decode + normalise.
    uploaded.seek(0)
    try:
        with Image.open(uploaded) as img:
            # Decompression-bomb guard, evaluated before .load() so a
            # malicious header asking for huge dimensions never reaches
            # the decoder.
            if img.width * img.height > MAX_INPUT_PIXELS:
                raise InvalidAvatarUpload(
                    "Imaginea are dimensiuni prea mari."
                )
            # Force a full decode so any pixel-data error surfaces here.
            img.load()
            img = ImageOps.exif_transpose(img)
            # `ImageOps.fit` does center-crop-then-resize in one pass
            # using LANCZOS — the standard "produce a square thumbnail"
            # recipe.
            img = ImageOps.fit(
                img, (OUTPUT_SIDE, OUTPUT_SIDE), Image.LANCZOS
            )
            if img.mode != "RGB":
                img = img.convert("RGB")
            buf = io.BytesIO()
            # Saving to a fresh buffer without passing `exif=`/`icc_profile=`
            # discards every metadata block; we keep `optimize=True` so the
            # JPEG isn't bloated.
            img.save(
                buf,
                format=OUTPUT_FORMAT,
                quality=JPEG_QUALITY,
                optimize=True,
            )
            return buf.getvalue(), OUTPUT_EXT
    except InvalidAvatarUpload:
        raise
    except (
        UnidentifiedImageError,
        Image.DecompressionBombError,
        OSError,
        ValueError,
    ):
        raise InvalidAvatarUpload(
            "Imaginea nu a putut fi procesată."
        ) from None
