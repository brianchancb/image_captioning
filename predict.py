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

