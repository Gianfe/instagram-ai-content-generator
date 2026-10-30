from datetime import datetime
from pathlib import Path

from instagram_content_creator.api import post_hello_world, upload_to_cloudinary
from instagram_content_creator.text_image import TextImageOptions, generate_text_image

MORNING_END_HOUR = 18  # before this hour counts as "mattina", after as "sera"


def post_current_time() -> None:
    """Generate an image with the current time, publish it to Instagram, then delete it locally."""
    now = datetime.now()
    is_morning = now.hour < MORNING_END_HOUR
    background_color = "white" if is_morning else "black"
    text_color = "black" if is_morning else "white"

    orario = now.strftime("%H:%M")
    text = f"Ciao, sono le ore {orario}"

    image_path = Path(f"orario-{now.strftime('%Y%m%d-%H%M%S')}.png")
    generate_text_image(
        text,
        image_path,
        TextImageOptions(background_color=background_color, text_color=text_color),
    )

    try:
        uploaded = upload_to_cloudinary(str(image_path), folder="instagram-automation")
        print(f"Immagine caricata su Cloudinary: {uploaded.download_url}")

        media_id = post_hello_world(uploaded.download_url, caption=text)
        print(f"Post pubblicato! Media id: {media_id}")
    finally:
        image_path.unlink(missing_ok=True)


if __name__ == "__main__":
    post_current_time()
