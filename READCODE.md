<h1>Code Breakdown</h1>

<p>The OCR BookFinder Web project is a web-based application designed to recognize text from images of book pages and identify the book based on the extracted text. The application utilizes Tesseract OCR for text extraction, OpenCV for image preprocessing, and the Google Books API for book identification. Users can upload an image of a book page, and the system will process it to display the extracted text and the best matching book from the Google Books database. This tool is particularly useful for identifying books based on pages or specific text snippets captured via images.</p>

<h2>Text Extraction from Image</h2>

<p>The extract_text function handles the OCR process using the Tesseract OCR engine. The process involves:</p>

<p>Reading the Image: The image is read using OpenCV.</p>

<p>Grayscale Conversion: The image is converted to grayscale to improve OCR accuracy.</p>

<p>Text Extraction: Tesseract OCR is used to extract text from the grayscale image.</p>

```py
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

```

<h2>Book Identification using Google Books API</h2>

<p>The get_best_match function is responsible for identifying the book that best matches the extracted text. The process involves:</p>

<p>Sending a Request to Google Books API: The extracted text is used as a query to search for books.</p>

<p>Processing the Response: The response is parsed to find the book with the highest relevance.</p>

<p>Returning the Best Match: The title and authors of the best matching book are returned.</p>

```py
import requests

def search_book(text):
    url = 'https://www.googleapis.com/books/v1/volumes'
    params = {
        'q': text,
        'maxResults': 10,
    }
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

    # Find the best match based on the highest relevance
    best_match = max(books, key=lambda x: x.get('relevance', 0))

    volume_info = best_match.get('volumeInfo', {})
    title = volume_info.get('title', 'No title')
    authors = volume_info.get('authors', ['Unknown author'])
    return f"{title}, Authors: {', '.join(authors)}"

```

<h2>Main Function</h2>

<p>The main function integrates both components. It takes an image path as input, extracts text from the image, and finds the best matching book. The extracted text and the best match are printed to the console.</p>

```py

def get_best_match(extracted_text):
    books = search_book(extracted_text)
    if not books:
        return "No matches found."

    # Find the best match based on the highest relevance
    best_match = max(books, key=lambda x: x.get('relevance', 0))

    volume_info = best_match.get('volumeInfo', {})
    title = volume_info.get('title', 'No title')
    authors = volume_info.get('authors', ['Unknown author'])
    return f"{title}, Authors: {', '.join(authors)}"

def main(image_path):
    # Extract text from the image
    extracted_text = extract_text(image_path)
    print(f"Extracted Text: \n\n{extracted_text}\n")

    # Get the best matching book using the Google Books API
    best_match = get_best_match(extracted_text)
    print(f"Best Match: {best_match}")

```

<h2>Deployment of OCR Bookfinder Application</h2>

<h3>Dockerfile</h3>

<p>The Dockerfile is used to containerize the OCR BookFinder application. It defines the environment and dependencies required for running the application:</p>

<pre><code>
# Use the official Python image
FROM python:3.10-slim

# Install Tesseract, OpenCV dependencies, and other necessary libraries
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variables
ENV FLASK_APP=app.py

# Expose port 5000
EXPOSE 5000

# Run the Flask app
CMD ["flask", "run", "--host=0.0.0.0"]
</code></pre>

<h3>Fly.io Configuration (fly.toml)</h3>
<p>The <code>fly.toml</code> file is used to configure the deployment of the Docker containerized application on Fly.io:</p>

<pre><code>
# fly.toml app configuration file generated for ocr-bookfinder on 2024-09-05T12:38:31-04:00
#
# See https://fly.io/docs/reference/configuration/ for information about how to use this file.
#

app = 'ocr-bookfinder'
primary_region = 'dfw'

[build]

[http_service]
  internal_port = 5000
  force_https = true
  auto_stop_machines = 'stop'
  auto_start_machines = true
  min_machines_running = 0
  processes = ['app']

[[vm]]
  memory = '1gb'
  cpu_kind = 'shared'
  cpus = 1
</code></pre>

<h2>Conclusion</h2>

<p>This program effectively combines OCR and web API technologies to identify the book corresponding to text extracted from an image. It leverages Tesseract OCR for text extraction and the Google Books API for book identification. This approach can be useful for various applications such as digitizing and cataloging printed materials.</p>

<div style="display: flex; justify-content: center; align-items: center;">
  <img src="https://i.imgur.com/OTuB77Y.gif" alt="BookPage" style="width: auto; height: 300px; margin: 20px;">
  
  <img src="https://i.imgur.com/bbSfVCY.png" alt="TranslatingText" style="width: auto; height: 300px; margin: 20px;">

