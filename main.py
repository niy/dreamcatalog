import os

from PIL import Image
from dotenv import load_dotenv
import streamlit as st
from rembg_api import Rembg
# from removebg_api import RemoveBgApi
from openai_api import OpenAiApi
from image_resizer import ImageResizer
import asyncio

# Load environment variables from .env file
load_dotenv()

# Set the layout of the Streamlit application
st.set_page_config(layout="wide")
st.title("Product Image Generator 🎨")

# col_api_keys_rbg, col_api_keys_oai = st.columns(2)
# Read API keys from user input filled with environment variables as default values\
# with col_api_keys_rbg:
#    remove_bg_api_key = st.text_input("Remove.bg API Key", value=os.getenv("REMOVE_BG_API_KEY", ""), type="password")
# with col_api_keys_oai:
openai_api_key = st.text_input("OpenAI API Key", value=os.getenv("OPENAI_API_KEY", ""), type="password")

# Create UI elements for file upload, product type selection, and scene definition
image_files = st.file_uploader("Upload Product Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

scene_definition = st.text_input("Scene Definition", max_chars=1000,
                                 placeholder="a swiss cheese plant on top of a table in a bright hotel room with a view of the ocean in the background",
                                 help="Enter a description of the scene you want to generate.")

# Add a selection box for the user to choose the background removal API
# api_options = ["Rembg (free)", "Remove.bg (paid)"]
# selected_api = st.selectbox("Choose background removal API:", api_options)

invalidate_cache = st.checkbox("Invalidate cache")
submit_button = st.button("Generate Images")


async def process_images():
    # Process the images with remove.bg API and extract masks
    bg_removed_pairs = await asyncio.gather(
        *[remove_bg_api.remove_background_and_return_img_pair(img, force_invalidate_cache=invalidate_cache) for img in
          resized_images]
    )

    # Use the masks to generate new images with DALL-E API
    async with OpenAiApi(openai_api_key) as openai_api:
        image_urls = await asyncio.gather(
            *[openai_api.generate_image_with_mask(original_image, no_bg_image, scene_definition) for
              original_image, no_bg_image in bg_removed_pairs]
        )
    return image_urls, bg_removed_pairs


if submit_button and image_files:
    # Initialize the ImageResizer class
    resizer = ImageResizer()
    # if selected_api == "Remove.bg":
    #     remove_bg_api = RemoveBgApi(remove_bg_api_key)
    # else:
    remove_bg_api = Rembg()

    resized_images = []
    processed = []

    with st.spinner("Processing images, please wait..."):
        # Create columns for the raw images, the images with the background removed, and the processed images
        col_raw_image, col_no_background, col_processed = st.columns(3)
        with col_raw_image:
            st.header("Raw Images")
            # Resize the input images
            for uploaded_file in image_files:
                uploaded_file.seek(0)
                img = Image.open(uploaded_file)
                resized_image = resizer.resize_to_square(img)
                resized_images.append(resized_image)
            for resized_image in resized_images:
                st.image(resized_image)

        # Run the async function to process and generate images
        generated_image_urls, bg_removed_pairs = asyncio.run(process_images())

        with col_no_background:
            st.header("Background Removed")
            for original_image, no_bg_image in bg_removed_pairs:
                st.image(no_bg_image)

        # Display the generated images to the user
        with col_processed:
            st.header("Generated Images")
            for url in generated_image_urls:
                st.image(url)

        st.success("Done!")
