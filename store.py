import sqlite3
import os
from PIL import Image
import streamlit as st
from predict import predict_caption

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