from instagram_content_creator.api import post_carousel


def main() -> None:
    image_urls = [
        "https://upload.wikimedia.org/wikipedia/commons/d/de/Colosseo_2020.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/d/de/Colosseo_2020.jpg",
    ]
    caption = "Ciao da Roma!"
    media_id = post_carousel(image_urls=image_urls, caption=caption)

    print(f"Carosello pubblicato! Media id: {media_id}")


if __name__ == "__main__":
    main()
