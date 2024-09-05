from flask import Flask, render_template, request, redirect, url_for
import cv2
import pytesseract
import os
import requests
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def extract_text(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(gray, config=custom_config)
    return text.strip()

def preprocess_text(text):
    import re
    import string
    text = re.sub(f"[{re.escape(string.punctuation)}]", "", text)
    text = text.lower()
    text = " ".join(text.split())
    return text

def search_book(text):
    url = 'https://www.googleapis.com/books/v1/volumes'
    params = {'q': text, 'maxResults': 10}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data.get('items', [])
    else:
        print(f"Error: {response.status_code}")
        return []

def get_best_match(extracted_text):
    books = search_book(extracted_text)
    if not books:
        return "No matches found."
    best_match = max(books, key=lambda x: x.get('relevance', 0))
    volume_info = best_match.get('volumeInfo', {})
    title = volume_info.get('title', 'No title')
    authors = volume_info.get('authors', ['Unknown author'])
    return f"{title}, Authors: {', '.join(authors)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                text = extract_text(file_path)
                processed_text = preprocess_text(text)
                best_match = get_best_match(processed_text)

                return render_template('result.html', text=text, best_match=best_match, image=filename)

    return render_template('index.html')

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
