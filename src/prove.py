from instagram_content_creator.api import post_with_location, post_hello_world


def main() -> None:
    image_url = "https://upload.wikimedia.org/wikipedia/commons/d/de/Colosseo_2020.jpg"
       
    
    caption = "Ciao da Roma!"
    location_id = "123456789"  # Sostituisci con un ID valido di Facebook Places.

    # media_id = post_with_location(
    #     image_url=image_url,
    #     location_id=location_id,
    #     caption=caption,
    # )
    
    media_id = post_hello_world(
        image_url=image_url,
        caption=caption
    )
    
    
    
    print(f"Post pubblicato! Media id: {media_id}")


if __name__ == "__main__":
    main()
