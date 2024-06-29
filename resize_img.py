from PIL import Image


def generate_image_preview(image_path, preview_path="C:\Michael\preview.jpg"):
    """
    Generate a 100x100 px image preview.

    :param image_path: Path to the original image file.
    :param preview_path: Path to save the preview image.
    """
    with Image.open(image_path) as img:
        # Resize the image to 100x100 pixels
        img = img.resize((100, 100))
        # Save the resized image
        img.save(preview_path)
        print(f"Preview image saved at {preview_path}")


# Example usage
generate_image_preview("C:\Michael\homer.jpg")
