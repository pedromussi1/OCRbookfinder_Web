
<h1 align="center">OCR Bookfinder Web</h1>

<p align="center">
  <a href="https://youtu.be/U1GcrE8YPWU"><img src="https://i.imgur.com/OTuB77Y.gif" alt="YouTube Demonstration" width="800"></a>
</p>

<p align="center">A web application that extracts text from book pages and finds what book it is from, powered by Flask, Tesseract, and Google Books API.</p>

<h3>In case you want to access my web application, it is hosted here: <a href="https://ocr-bookfinder.fly.dev/">https://ocr-bookfinder.fly.dev/</a></h3>

<h2>Description</h2>

<p>The OCR Translator Web project is a web-based application designed to recognize text from images and translate it into various languages. The application leverages Tesseract OCR for text extraction, OpenCV for image preprocessing, and Azure Translation API for language translation. Users can upload an image containing text, and the system will process it to display the extracted and translated text. This tool is particularly useful for translating foreign documents, street signs, or any text captured via images.</p>

<h2>Languages and Utilities Used</h2>
<ul>
    <li><b>Flask:</b> Serves as the backbone of the web application, handling routing, user inputs, and rendering HTML templates.</li>
    <li><b>Python:</b> The primary language used for integrating various functionalities like OCR and translation.</li>
    <li><b>OpenCV:</b> Handles preprocessing of images, such as converting images to grayscale and preparing them for OCR processing.</li>
    <li><b>Tesseract OCR:</b> The main technology for recognizing text from images, capable of handling multiple languages.</li>
    <li><b>pytesseract:</b> A Python wrapper for Tesseract, simplifying the integration of OCR functionalities within the application.</li>
    <li><b>Azure Translation API:</b> Used to translate the extracted text into the desired target language.</li>
    <li><b>HTML/CSS:</b> Creates the frontend of the application, providing a simple and intuitive user interface.</li>
</ul>

<h2>Environments Used</h2>
<ul>
  <li><b>Windows 11</b></li>
  <li><b>Visual Studio Code</b></li>
</ul>

<h2>Installation</h2>
<ol>
    <li><strong>Clone the Repository:</strong>
        <pre><code>git clone https://github.com/yourusername/ocr-translator-web.git
cd ocr-translator-web</code></pre>
    </li>
    <li><strong>Create and Activate a Virtual Environment:</strong>
        <pre><code>python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`</code></pre>
    </li>
    <li><strong>Install Dependencies:</strong>
        <pre><code>pip install -r requirements.txt</code></pre>
    </li>
    <li><strong>Configure Azure API Key:</strong>
        <ul>
            <li>Set up your Azure Translation API key and endpoint in a configuration file or as environment variables.</li>
        </ul>
    </li>
    <li><strong>Run the Application:</strong>
        <pre><code>python app.py</code></pre>
        The application will start and be accessible at <code>http://127.0.0.1:5000/</code>.
    </li>
</ol>



<h2>Usage</h2>
<ol>
    <li>Open the application in your web browser.</li>
    <li>Upload an image with text by selecting a file from your local device.</li>
    <li>Click the "Upload and Translate" button to extract and translate the text from the image.</li>
    <li>The original image, processed image, extracted text, and translated text will be displayed on the results page.</li>
</ol>

<h2>Code Structure</h2>
<ul>
    <li><strong>app.py:</strong> Main application file that contains routes, image processing logic, and OCR/translation functionalities.</li>
    <li><strong>static/:</strong> Contains static files such as uploaded images and stylesheets.</li>
    <li><strong>templates/:</strong> HTML templates used for rendering the web pages.</li>
    <li><strong>uploads/:</strong> Stores uploaded images for processing.</li>
    <li><strong>Dockerfile:</strong> Defines the Docker configuration for containerizing the application.</li>
</ul>

<h2>Known Issues</h2>
<ul>
    <li>Images with low quality or poor lighting may result in inaccurate text extraction.</li>
    <li>Translation accuracy depends on the language model used by Azure Translator.</li>
</ul>

<h2>Contributing</h2>
<p>Contributions are welcome! Please fork the repository, create a new branch, and submit a pull request with your changes. For major changes, please open an issue first to discuss what you would like to change.</p>

<h2>Deployment</h2>
<p>The application uses Docker for containerization, ensuring consistent environments across different platforms. Fly.io is used for deploying the application, providing a scalable and globally distributed infrastructure for web hosting.</p>

<p>

<h2>
<a href="https://github.com/yourusername/OCRtranslator_web/blob/main/READCODE.md">Code Breakdown Here!</a>
</h2>

<h3>Upload Image</h3>

<p align="center">
  <kbd><img src="https://i.imgur.com/tYxAQBd.png" alt="Upload Image" width="900"></kbd>
</p>

<p>The main page allows the user to upload an image containing text. The application then processes this image to extract and translate the text.</p>

<hr>

<h3>Processed Image and Results</h3>

<p align="center">
  <kbd><img src="https://i.imgur.com/4XBR3YJ.png" alt="Results" width="900"></kbd>
</p>

<p>After processing, the application displays the original and processed images, along with the recognized and translated text.</p>

