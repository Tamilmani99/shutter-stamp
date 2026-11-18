import io
import os
import random
import textwrap
import uuid

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from PIL import (
    Image,
    ImageDraw,
    ImageEnhance,
    ImageFilter,
    ImageFont,
    ImageOps,
)

from PIL.Image import DecompressionBombError

Image.MAX_IMAGE_PIXELS = 40_000_000


app = FastAPI(title="Shutter Stamp API")


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))

FRONTEND_PUBLIC_DIR = os.path.abspath(
    os.path.join(
        BACKEND_DIR,
        "..",
        "frontend",
        "public",
    )
)

STAMP_DIR = os.path.join(
    FRONTEND_PUBLIC_DIR,
    "postcard",
)

# ---------------------------------------------------------
# APPLICATION CONFIGURATION
# ---------------------------------------------------------

MAX_FILE_SIZE = int(
    os.getenv("MAX_FILE_SIZE", 20 * 1024 * 1024)
)


# ---------------------------------------------------------
# FONT HELPERS
# ---------------------------------------------------------

# ---------------------------------------------------------
# FONTS
# ---------------------------------------------------------

SCRIPT_FONT_PATHS = [
    os.path.join(BACKEND_DIR, "fonts", "segoescb.ttf"),
]

TIMES_BOLD_FONT_PATH = os.path.join(
    BACKEND_DIR,
    "fonts",
    "timesbd.ttf",
)



def get_script_font(size: int):
    for path in SCRIPT_FONT_PATHS:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(
                    path,
                    size,
                )
            except Exception:
                pass

    return ImageFont.load_default()


def get_times_bold_font(size: int):
    if os.path.exists(TIMES_BOLD_FONT_PATH):
        try:
            return ImageFont.truetype(
                TIMES_BOLD_FONT_PATH,
                size,
            )
        except Exception:
            pass

    return ImageFont.load_default()


# ---------------------------------------------------------
# LO-FI PHOTO EFFECT
# ---------------------------------------------------------

# ---------------------------------------------------------
# LO-FI PHOTO EFFECT
# ---------------------------------------------------------

def apply_lofi(image: Image.Image) -> Image.Image:
    image = image.convert("RGB")

    original_width, original_height = image.size

    # Reduce resolution strongly to create the
    # imperfect low-resolution photographic character.
    target_width = min(850, original_width)

    target_height = max(
        1,
        int(
            original_height
            * (target_width / original_width)
        ),
    )

    image = image.resize(
        (
            target_width,
            target_height,
        ),
        Image.Resampling.LANCZOS,
    )

    # Stronger contrast
    image = ImageEnhance.Contrast(
        image
    ).enhance(1.35)

    # Slightly stronger colour
    image = ImageEnhance.Color(
        image
    ).enhance(1.18)

    # Slight sharpening gives the
    # rough printed-photo character.
    image = image.filter(
        ImageFilter.SHARPEN
    )

    # Reduce the colour palette heavily.
    # This is important for the vintage
    # low-resolution / dithered appearance.
    image = image.quantize(
        colors=32,
        method=Image.Quantize.MEDIANCUT,
    )

    # Convert back to RGB while preserving
    # the intentionally limited palette.
    image = image.convert("RGB")

    # Add subtle grain/noise.
    pixels = image.load()

    grain_amount = 12

    for y in range(image.height):
        for x in range(image.width):
            r, g, b = pixels[x, y]

            noise = random.randint(
                -grain_amount,
                grain_amount,
            )

            pixels[x, y] = (
                max(
                    0,
                    min(
                        255,
                        r + noise,
                    ),
                ),
                max(
                    0,
                    min(
                        255,
                        g + noise,
                    ),
                ),
                max(
                    0,
                    min(
                        255,
                        b + noise,
                    ),
                ),
            )

    return image


# ---------------------------------------------------------
# RANDOM REAL STAMP
# ---------------------------------------------------------

def load_random_stamp():
    stamp_files = [
        f"stamp-{number}.png"
        for number in range(1, 11)
    ]

    random.shuffle(stamp_files)

    for filename in stamp_files:
        path = os.path.join(
            STAMP_DIR,
            filename,
        )

        if os.path.exists(path):
            try:
                stamp = Image.open(path).convert("RGBA")

                print(
                    f"Using stamp: {filename}"
                )

                return stamp

            except Exception as error:
                print(
                    f"Could not load {filename}: {error}"
                )

    print(
        "WARNING: No stamp image was found."
    )

    return None


# ---------------------------------------------------------
# ADD REAL STAMP TO POSTCARD
# ---------------------------------------------------------

def add_real_stamp(canvas: Image.Image):
    stamp = load_random_stamp()

    if stamp is None:
        return canvas

    canvas = canvas.convert("RGBA")

    canvas_width, canvas_height = canvas.size

    # Stamp size is based on the postcard dimensions
    max_stamp_size = max(
        90,
        min(canvas_width, canvas_height) // 8,
    )

    stamp.thumbnail(
        (
            max_stamp_size,
            max_stamp_size,
        ),
        Image.Resampling.LANCZOS,
    )

    # Top-right placement
    right_margin = max(
        28,
        canvas_width // 30,
    )

    top_margin = max(
        28,
        canvas_height // 30,
    )

    # Give the stamp a tiny natural rotation
    rotation = random.choice(
        [-5, -3, 2, 4]
    )

    rotated_stamp = stamp.rotate(
        rotation,
        expand=True,
        resample=Image.Resampling.BICUBIC,
    )

    rotated_width, rotated_height = (
        rotated_stamp.size
    )

    stamp_x = (
        canvas_width
        - rotated_width
        - right_margin
    )

    stamp_y = top_margin

    canvas.alpha_composite(
        rotated_stamp,
        (
            int(stamp_x),
            int(stamp_y),
        ),
    )

    return canvas


# ---------------------------------------------------------
# PLACE + YEAR
# ---------------------------------------------------------



def draw_place_and_year(
    canvas: Image.Image,
    place: str,
    year: str,
    photo_bottom: int,
):
    draw = ImageDraw.Draw(canvas)

    width, height = canvas.size

    font_size = max(
        28,
        min(width, height) // 23,
    )

    font = get_times_bold_font(
        font_size
    )

    if place and year:
        text = f"{place.strip()} {year.strip()}"
    elif place:
        text = place.strip()
    elif year:
        text = year.strip()
    else:
        return canvas

    margin = max(
        35,
        width // 25,
    )

    padding_x = 12
    padding_y = 8

    max_text_width = (
        width
        - (margin * 2)
        - (padding_x * 2)
    )

    def get_text_width(value):
        bbox = draw.textbbox(
            (0, 0),
            value,
            font=font,
        )

        return bbox[2] - bbox[0]

    words = text.split()

    lines = []
    current_line = ""

    for word in words:
        parts = []
        remaining = word

        while remaining:
            if get_text_width(remaining) <= max_text_width:
                parts.append(remaining)
                break

            chunk = ""

            for character in remaining:
                candidate = chunk + character

                if get_text_width(candidate) > max_text_width:
                    break

                chunk = candidate

            if not chunk:
                chunk = remaining[0]

            parts.append(chunk)
            remaining = remaining[len(chunk):]

        for part in parts:
            candidate = (
                f"{current_line} {part}".strip()
            )

            if (
                current_line
                and get_text_width(candidate) > max_text_width
            ):
                lines.append(current_line)
                current_line = part
            else:
                current_line = candidate

    if current_line:
        lines.append(current_line)

    line_height = font_size + 8

    text_height = len(lines) * line_height

    text_width = max(
        get_text_width(line)
        for line in lines
    )

    x = (
        width
        - margin
        - padding_x
        - text_width
    )

    # Anchor the backing to the photograph's bottom edge.
    y = (
        photo_bottom
        - padding_y
        - text_height
    )

    draw.rounded_rectangle(
        (
            x - padding_x,
            y - padding_y,
            x + text_width + padding_x,
            photo_bottom,
        ),
        radius=5,
        fill=(
            244,
            236,
            215,
            220,
        ),
    )

    for line in lines:
        line_width = get_text_width(line)

        draw.text(
            (
                width - margin - padding_x - line_width,
                y,
            ),
            line,
            font=font,
            fill=(
                60,
                50,
                40,
            ),
        )

        y += line_height

    return canvas



# ---------------------------------------------------------
# OPTIONAL LO-FI MESSAGE
# ---------------------------------------------------------


def draw_lofi_message(
    image: Image.Image,
    message: str,
):
    if not message.strip():
        return image.convert("RGB")

    image = image.convert("RGB")

    padding = max(
        28,
        min(
            image.width,
            image.height,
        ) // 20,
    )

    max_text_width = max(
        1,
        image.width - (padding * 2),
    )

    draw = ImageDraw.Draw(image)

    font_size = max(
        27,
        min(
            image.width,
            image.height,
        ) // 24,
    )

    font = get_script_font(
        font_size
    )

    def get_text_width(text):
        bbox = draw.textbbox(
            (0, 0),
            text,
            font=font,
        )

        return bbox[2] - bbox[0]

    # Wrap the message and break long words.
    words = message.strip().split()

    lines = []
    current_line = ""

    for word in words:
        word_parts = []
        remaining_word = word

        while remaining_word:
            if get_text_width(remaining_word) <= max_text_width:
                word_parts.append(remaining_word)
                break

            chunk = ""

            for character in remaining_word:
                candidate = chunk + character

                if get_text_width(candidate) > max_text_width:
                    break

                chunk = candidate

            if not chunk:
                chunk = remaining_word[0]

            word_parts.append(chunk)
            remaining_word = remaining_word[len(chunk):]

        for part in word_parts:
            candidate = (
                f"{current_line} {part}".strip()
            )

            if (
                current_line
                and get_text_width(candidate) > max_text_width
            ):
                lines.append(current_line)
                current_line = part
            else:
                current_line = candidate

    if current_line:
        lines.append(current_line)

    # Calculate the required message panel height.
    line_height = font_size + 12

    total_height = (
        len(lines) * line_height
    )

    message_area = max(
        125,
        image.height // 5,
        total_height + 40,
    )

    # Create a canvas with enough room for every line.
    canvas = Image.new(
        "RGB",
        (
            image.width,
            image.height + message_area,
        ),
        (
            244,
            236,
            215,
        ),
    )

    canvas.paste(
        image,
        (0, 0),
    )

    draw = ImageDraw.Draw(
        canvas
    )

    start_y = (
        image.height
        + (message_area - total_height) // 2
    )

    for line in lines:
        bbox = draw.textbbox(
            (0, 0),
            line,
            font=font,
        )

        line_width = (
            bbox[2] - bbox[0]
        )

        x = (
            image.width - line_width
        ) // 2

        # Warm shadow.
        draw.text(
            (
                x + 1,
                start_y + 1,
            ),
            line,
            font=font,
            fill=(
                150,
                137,
                115,
            ),
        )

        # Main message.
        draw.text(
            (
                x,
                start_y,
            ),
            line,
            font=font,
            fill=(
                70,
                57,
                43,
            ),
        )

        start_y += line_height

    return canvas


# ---------------------------------------------------------
# POSTCARD
# ---------------------------------------------------------

def create_postcard(
    image: Image.Image,
    place: str,
    year: str,
):
    # Postcard uses the same Lo-Fi treatment
    image = apply_lofi(image)

    image = image.convert("RGB")

    border = max(
        24,
        min(image.width, image.height) // 18,
    )

    canvas = Image.new(
        "RGBA",
        (
            image.width + border * 2,
            image.height + border * 2,
        ),
        (244, 236, 215, 255),
    )

    canvas.paste(
        image,
        (border, border),
    )

    # Real random stamp
    canvas = add_real_stamp(canvas)

    # Place and year
    canvas = draw_place_and_year(
        canvas,
        place,
        year,
        border + image.height,
)

    return canvas.convert("RGB")


# ---------------------------------------------------------
# POSTCARD WITH LETTER
# ---------------------------------------------------------

def create_postcard_with_letter(
    image: Image.Image,
    place: str,
    year: str,
    message: str,
):
    postcard = create_postcard(
        image,
        place,
        year,
    )

    postcard = postcard.convert("RGB")

    letter_height = max(
        170,
        postcard.width // 5,
    )

    canvas = Image.new(
        "RGB",
        (
            postcard.width,
            postcard.height + letter_height,
        ),
        (244, 236, 215),
    )

    canvas.paste(
        postcard,
        (0, 0),
    )

    draw = ImageDraw.Draw(canvas)

    # Small separator line
    line_y = postcard.height

    draw.line(
        (
            25,
            line_y,
            canvas.width - 25,
            line_y,
        ),
        fill=(190, 177, 151),
        width=1,
    )

    if message.strip():
        font_size = max(
            19,
            min(
                postcard.width,
                postcard.height,
            ) // 34,
        )

        font = get_script_font(font_size)

        max_chars = max(
            28,
            postcard.width // 19,
        )

        lines = textwrap.wrap(
            message.strip(),
            width=max_chars,
        )

        line_height = (
            font_size + 9
        )

        total_height = (
            len(lines) * line_height
        )

        start_y = (
            line_y
            + (
                letter_height
                - total_height
            ) // 2
        )

        for line in lines:
            bbox = draw.textbbox(
                (0, 0),
                line,
                font=font,
            )

            line_width = (
                bbox[2] - bbox[0]
            )

            x = (
                canvas.width
                - line_width
            ) // 2

            draw.text(
                (x, start_y),
                line,
                font=font,
                fill=(76, 64, 50),
            )

            start_y += line_height

    return canvas


# ---------------------------------------------------------
# STYLE PROCESSING
# ---------------------------------------------------------

def process_image(
    image: Image.Image,
    style: str,
    place: str,
    year: str,
    message: str,
):
    if style == "lofi":
        result = apply_lofi(image)

        result = draw_lofi_message(
            result,
            message,
        )

        return result

    if style == "postcard":
        return create_postcard(
            image,
            place,
            year,
        )

    if style == "with-love":
        return create_postcard_with_letter(
            image,
            place,
            year,
            message,
        )

    raise ValueError("Unsupported image style.")



# ---------------------------------------------------------
# API
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "Shutter Stamp API is running"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/api/process")
async def process(
    file: UploadFile = File(...),
    style: str = Form(...),
    place: str = Form(""),
    year: str = Form(""),
    message: str = Form(""),
):
    allowed_styles = {
        "lofi",
        "postcard",
        "with-love",
    }

    if style not in allowed_styles:
        raise HTTPException(
            status_code=400,
            detail="Invalid image style selected."
        )
    # Validate message length
    if len(message) > 200:
         raise HTTPException(
             status_code=400,
             detail="Message must be 200 characters or fewer."
    )
    # Validate place name
    if len(place.strip()) > 80: 
         raise HTTPException(
             status_code=400,
             detail="Place name must be 80 characters or fewer."
    )

    # Validate year
    if year.strip() and not (
       year.strip().isdigit()
       and len(year.strip()) == 4
):
       raise HTTPException(
           status_code=400,
           detail="Please enter a valid four-digit year."
    )
    # -----------------------------------------------------
    # BACKEND FILE VALIDATION
    # -----------------------------------------------------

    allowed_types = {
        "image/jpeg",
        "image/jpg",
    }

    if file.content_type not in allowed_types:
     raise HTTPException(
        status_code=415,
        detail="Only JPG and JPEG images are supported."
    )

    contents = await file.read(MAX_FILE_SIZE + 1)

    # Check maximum upload size
    if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
        status_code=413,
        detail="Image size must be 20 MB or smaller."
    )
    

    try:
        image = Image.open(
            io.BytesIO(contents)
        )

        # Prevent excessively large images
        MAX_IMAGE_PIXELS = 40_000_000

        if image.width * image.height > MAX_IMAGE_PIXELS:
            raise HTTPException(
                status_code=413,
                detail="Image dimensions are too large."
            )

        # Verify the actual image format
        if image.format != "JPEG":
            raise HTTPException(
                status_code=415,
                detail="Only genuine JPG and JPEG images are supported."
            )

        image = ImageOps.exif_transpose(
            image
        )

        result = process_image(
            image=image,
            style=style,
            place=place,
            year=year,
            message=message,
        )

                # RETURN PROCESSED IMAGE DIRECTLY
        image_buffer = io.BytesIO()

        result.save(
            image_buffer,
            format="JPEG",
            quality=94,
            optimize=True,
        )

        image_buffer.seek(0)

        return Response(
            content=image_buffer.getvalue(),
            media_type="image/jpeg",
            headers={
                "Content-Disposition": (
                    "inline; "
                    "filename=shutter-stamp-result.jpg"
                )
            },
        )

    except HTTPException:
        raise

    except DecompressionBombError:
        raise HTTPException(
            status_code=413,
            detail="Image dimensions are too large."
        )

    except Exception as error:
        print(
            f"Image processing error: {error}"
        )

        raise HTTPException(
            status_code=500,
            detail="Image processing failed. Please try again."
        )
    