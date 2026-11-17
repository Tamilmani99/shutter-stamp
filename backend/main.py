import io
import os
import random
import textwrap

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from PIL import (
    Image,
    ImageDraw,
    ImageEnhance,
    ImageFilter,
    ImageFont,
    ImageOps,
)


app = FastAPI(title="Shutter Stamp API")


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
):
    draw = ImageDraw.Draw(canvas)

    width, height = canvas.size

    # Larger than before
    font_size = max(
        28,
        min(width, height) // 23,
    )

    # Times New Roman Bold
    font = get_times_bold_font(
        font_size
    )

    # IMPORTANT:
    # No dot / bullet between place and year.
    if place and year:
        text = f"{place} {year}"
    elif place:
        text = place
    elif year:
        text = year
    else:
        return canvas

    bbox = draw.textbbox(
        (0, 0),
        text,
        font=font,
    )

    text_width = (
        bbox[2] - bbox[0]
    )

    text_height = (
        bbox[3] - bbox[1]
    )

    x = (
        width
        - text_width
        - max(
            35,
            width // 25,
        )
    )

    y = (
        height
        - text_height
        - max(
            30,
            height // 28,
        )
    )

    # Small warm paper backing
    padding_x = 12
    padding_y = 8

    draw.rounded_rectangle(
        (
            x - padding_x,
            y - padding_y,
            x + text_width + padding_x,
            y + text_height + padding_y,
        ),
        radius=5,
        fill=(
            244,
            236,
            215,
            220,
        ),
    )

    draw.text(
        (x, y),
        text,
        font=font,
        fill=(
            60,
            50,
            40,
        ),
    )

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

    message_area = max(
        125,
        image.height // 5,
    )

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

    # Larger output text
    font_size = max(
        27,
        min(
            image.width,
            image.height,
        ) // 24,
    )

    # Bold script-style font
    font = get_script_font(
        font_size
    )

    max_chars = max(
        22,
        image.width // 16,
    )

    lines = textwrap.wrap(
        message.strip(),
        width=max_chars,
    )

    line_height = (
        font_size + 12
    )

    total_height = (
        len(lines)
        * line_height
    )

    start_y = (
        image.height
        + (
            message_area
            - total_height
        )
        // 2
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
            image.width
            - line_width
        ) // 2

        # Slight warm shadow underneath
        # makes the script easier to read.
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

    return image.convert("RGB")


# ---------------------------------------------------------
# API
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "Shutter Stamp API is running"
    }


@app.post("/api/process")
async def process(
    file: UploadFile = File(...),
    style: str = Form(...),
    place: str = Form(""),
    year: str = Form(""),
    message: str = Form(""),
):
    # -----------------------------------------------------
    # BACKEND FILE VALIDATION
    # -----------------------------------------------------

    allowed_types = {
        "image/jpeg",
        "image/jpg",
    }

    if file.content_type not in allowed_types:
        return {
            "error": "Only JPG and JPEG images are supported."
        }

    contents = await file.read()

    # 10 MB maximum
    max_file_size = 10 * 1024 * 1024

    if len(contents) > max_file_size:
        return {
            "error": "Image size must be 10 MB or smaller."
        }

    try:
        image = Image.open(
            io.BytesIO(contents)
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

        output = io.BytesIO()

        result.save(
            output,
            format="JPEG",
            quality=94,
            optimize=True,
        )

        output.seek(0)

        return StreamingResponse(
            output,
            media_type="image/jpeg",
            headers={
                "Content-Disposition": (
                    "inline; "
                    "filename=shutter-stamp-result.jpg"
                )
            },
        )

    except Exception as error:
        print(
            f"Image processing error: {error}"
        )

        return {
            "error": str(error)
        }