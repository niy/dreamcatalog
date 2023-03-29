from PIL import Image


class ImageResizer:

    @staticmethod
    def resize_to_square(img: Image, size: int = 512) -> Image:
        """
        Resize the image to a square with the given size (width and height).

        :param img: The image as a BytesIO object to be resized.
        :param size: The desired width and height of the output image.

        :return: The resized image as a BytesIO object.
        """
        img.thumbnail((size, size), Image.ANTIALIAS)

        if img.width != img.height:
            original_img = img.copy()
            # Create a new blank transparent image with the desired size
            img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            # Calculate the position to paste the resized image
            paste_x = (size - original_img.width) // 2
            paste_y = (size - original_img.height) // 2
            img.paste(original_img, (paste_x, paste_y))

        # Resize the cropped image to the desired size
        img = img.resize((size, size), Image.ANTIALIAS)

        return img
