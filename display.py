import sqlite3
import os
from PIL import Image
import streamlit as st

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
