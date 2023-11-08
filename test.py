import streamlit as st
from PIL import Image
import io
import os
import sqlite3
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
import torch

# Load the model and tokenizer
model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
feature_extractor = ViTImageProcessor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

max_length = 16
num_beams = 4
gen_kwargs = {"max_length": max_length, "num_beams": num_beams}

# Create a database and table to store image path and caption
conn = sqlite3.connect('database1.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS image_captions (
        id INTEGER PRIMARY KEY,
        name TEXT,
        image_path TEXT,
        caption TEXT
    )
''')
conn.commit()
conn.close()

# Function to predict the caption for an image
def predict_caption(image):
    if image.format == "PNG" or image.format == 'png':
        # Convert PNG to JPEG
        image = image.convert("RGB")
    pixel_values = feature_extractor(images=image, return_tensors="pt").pixel_values
    pixel_values = pixel_values.to(device)

    output_ids = model.generate(pixel_values, **gen_kwargs)

    preds = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
    preds = [pred.strip() for pred in preds]
    return preds[0]

# Function to store the image path and caption in the database
def store_image_and_caption(name, uploaded_image):
    conn = sqlite3.connect('database1.db')
    cursor = conn.cursor()
    try:
        # Create a directory to save the images if it doesn't exist
        os.makedirs("images", exist_ok=True)

        # Generate a unique file path for the image
        image_path = f"images/{name}.jpg"

        # Save the uploaded image as a file
        image = Image.open(uploaded_image)
        if image.mode != "RGB":
            image = image.convert("RGB")
        image.save(image_path, format="JPEG")

        # Generate a caption for the image
        caption = predict_caption(image)

        cursor.execute("INSERT INTO image_captions (name, image_path, caption) VALUES (?, ?, ?)", (name, image_path, caption))
        conn.commit()
        st.success("Image path and caption stored successfully.")
    except sqlite3.Error as e:
        st.error(f"Error storing data: {e}")
    finally:
        conn.close()

# Function to fetch and display images and captions by name
def display_images_and_captions_by_name(input_str = None):
    conn = sqlite3.connect('database1.db')
    cursor = conn.cursor()
    try:
        if input_str:
            cursor.execute("SELECT image_path, caption FROM image_captions WHERE name LIKE ? OR caption LIKE ?",
                           ('%' + input_str + '%', '%' + input_str + '%'))
        else:
            cursor.execute("SELECT image_path, caption FROM image_captions")

        results = cursor.fetchall()
        if results:
            for result in results:

                image_path, caption = result
                if os.path.exists(image_path):  # Make sure image_path is a string representing a file path
                    image = Image.open(image_path)
                    st.image(image, caption=f"Image with Name: {input_str}", use_column_width=True)
                    st.write("Caption:", caption)
                else:
                    st.write("Image not found for the specified name.")
        else:
            st.write("Image not found for the specified name.")
    except sqlite3.Error as e:
        st.error(f"Error fetching data: {e}")
    finally:
        conn.close()

# Streamlit app
def main():
    st.title("Image Storage, Retrieval, and Captioning")

    # Upload image through Streamlit
    uploaded_image = st.file_uploader("Upload an image...", type=["jpg", "png", "jpeg", "JPG", "PNG", "JPEG"])

    if uploaded_image is not None:
        image = Image.open(uploaded_image)  # Ensure image is a PIL image
        st.image(image, caption="Uploaded Image", use_column_width=True)

        if st.button("Generate Caption"):
            caption = predict_caption(image)
            st.write("Generated Caption:", caption)

        name = st.text_input("Enter a unique name for the image:")
        if st.button("Store Image and Caption"):
            store_image_and_caption(name, uploaded_image)

    st.subheader("Fetch Images and Captions by Name")
    name = st.text_input("Enter the name to fetch images and captions:")
    if st.button("Fetch Images and Captions"):
        display_images_and_captions_by_name(name)

if __name__ == "__main__":
    main()

