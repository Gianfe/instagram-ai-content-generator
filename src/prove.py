from instagram_content_creator.api import post_carousel, upload_to_cloudinary
from instagram_content_creator.cloudinary_storage import generate_image


def upload_file_example(file_path: str) -> None:
    uploaded = upload_to_cloudinary(file_path)
    print(f"File caricato su Cloudinary: {uploaded.file_name}")
    print(f"Link per il download: {uploaded.download_url}")


def generate_image_example(
    prompt: str, public_id: str | None = None, folder: str | None = None
) -> str:
    generated = generate_image(prompt, public_id=public_id, folder=folder)
    print(f"Immagine generata: {generated.public_id}")
    print(f"Link per il download: {generated.download_url}")
    return generated.download_url

def main() -> None:
    image_urls = [
        "https://upload.wikimedia.org/wikipedia/commons/d/de/Colosseo_2020.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/d/de/Colosseo_2020.jpg",
    ]
    caption = "Ciao da Roma!"
    media_id = post_carousel(image_urls=image_urls, caption=caption)

    print(f"Carosello pubblicato! Media id: {media_id}")


if __name__ == "__main__":
    #main()
    #upload_file_example("C:\\xxx\\instagram-ai-content-generator\\README.md")
    url = generate_image_example(
        "un uomo su una thriumph tiger 800 del 2019 bianca",
        public_id="uomo-triumph-tiger-800-bianca",
    )
    
    image_urls = [
            url,
            "https://upload.wikimedia.org/wikipedia/commons/d/de/Colosseo_2020.jpg"
        ]
    caption = "Ciao @gianfmeloni"
    media_id = post_carousel(image_urls=image_urls, caption=caption)
    
    print(f"Carosello pubblicato! Media id: {media_id}")
