from io import BytesIO

import openai
from PIL import Image


class OpenAiApi:
    def __init__(self, api_key):
        self.api_key = api_key

    async def __aenter__(self):
        openai.api_key = self.api_key
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    @staticmethod
    async def generate_images_with_mask(img: Image, mask: Image, prompt, variations_no=5) -> list[str]:
        """
        Generate an image with the given mask using the DALL-E API.

        Args:
            :param img: (PIL.Image.Image) The input image.
            :param mask: (PIL.Image.Image) The mask to be used in the generated image.
            :param prompt: (str) The prompt to be used in DALL-E API.
            :param variations_no: (int) The number of variations to be generated.

        Returns:
            list[str]: A list of URLs of the generated images (based on the number of variations).
        """
        img_bytes = BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        mask_bytes = BytesIO()
        mask.save(mask_bytes, format="PNG")
        mask_bytes.seek(0)

        response = openai.Image.create_edit(
            image=img_bytes,
            mask=mask_bytes,
            prompt=prompt,
            n=variations_no,
            size="512x512"
        )

        return [image['url'] for image in response['data']]
