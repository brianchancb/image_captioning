import streamlit as st
from PIL import Image
from predict import predict_caption
from store import store_image_and_caption
from display import display_images_and_captions_by_name


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