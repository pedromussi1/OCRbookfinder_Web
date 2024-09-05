
<h1 align="center">OCR Bookfinder Web</h1>

<p align="center">
  <a href="https://youtu.be/U1GcrE8YPWU"><img src="https://i.imgur.com/OTuB77Y.gif" alt="YouTube Demonstration" width="800"></a>
</p>

<p align="center">A web application that extracts text from book pages and finds what book it is from, powered by Flask, Tesseract, and Google Books API.</p>

<h3>In case you want to access my web application, it is hosted here: <a href="https://ocr-bookfinder.fly.dev/">https://ocr-bookfinder.fly.dev/</a></h3>

<h2>Description</h2>
<p>The OCR BookFinder Web project is a web-based application designed to recognize text from images of book pages and identify the book based on the extracted text. The application utilizes Tesseract OCR for text extraction, OpenCV for image preprocessing, and the Google Books API for book identification. Users can upload an image of a book page, and the system will process it to display the extracted text and the best matching book from the Google Books database. This tool is particularly useful for identifying books based on pages or specific text snippets captured via images.</p>

<h2>Languages and Utilities Used</h2>
<ul>
    <li><b>Flask:</b> Serves as the backbone of the web application, handling routing, user inputs, and rendering HTML templates.</li>
    <li><b>Python:</b> The primary language used for integrating various functionalities like OCR and book identification.</li>
    <li><b>OpenCV:</b> Handles preprocessing of images, such as converting images to grayscale and preparing them for OCR processing.</li>
    <li><b>Tesseract OCR:</b> The main technology for recognizing text from images, capable of handling multiple languages.</li>
    <li><b>pytesseract:</b> A Python wrapper for Tesseract, simplifying the integration of OCR functionalities within the application.</li>
    <li><b>Google Books API:</b> Used to identify books based on the extracted text from the images.</li>
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
        <pre><code>git clone https://github.com/yourusername/ocr-bookfinder-web.git
cd ocr-bookfinder-web</code></pre>
    </li>
    <li><strong>Create and Activate a Virtual Environment:</strong>
        <pre><code>python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`</code></pre>
    </li>
    <li><strong>Install Dependencies:</strong>
        <pre><code>pip install -r requirements.txt</code></pre>
    </li>
    <li><strong>Configure Google Books API Key:</strong>
        <ul>
            <li>Set up your Google Books API key in a configuration file or as environment variables.</li>
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
    <li>Upload an image of a book page by selecting a file from your local device.</li>
    <li>Click the "Submit" button to extract text and identify the book from the image.</li>
    <li>The original image, extracted text, and the best matching book information will be displayed on the results page.</li>
</ol>

<h2>Code Structure</h2>
<ul>
    <li><strong>app.py:</strong> Main application file that contains routes, image processing logic, and OCR/book identification functionalities.</li>
    <li><strong>static/:</strong> Contains static files such as uploaded images and stylesheets.</li>
    <li><strong>templates/:</strong> HTML templates used for rendering the web pages.</li>
    <li><strong>uploads/:</strong> Stores uploaded images for processing.</li>
</ul>

<h2>Known Issues</h2>
<ul>
    <li>Images with low quality or poor lighting may result in inaccurate text extraction.</li>
    <li>The accuracy of book identification depends on the relevance of the extracted text and the Google Books database.</li>
</ul>

<h2>Contributing</h2>
<p>Contributions are welcome! Please fork the repository, create a new branch, and submit a pull request with your changes. For major changes, please open an issue first to discuss what you would like to change.</p>

<h2>Deployment</h2>
<p>The application uses Docker for containerization, ensuring consistent environments across different platforms. Fly.io is used for deploying the application, providing a scalable and globally distributed infrastructure for web hosting..</p>

<h2><a href="https://github.com/yourusername/ocr-bookfinder-web/blob/main/READCODE.md">Code Breakdown Here!</a></h2>

<h3>Upload Image</h3>
<p align="center">
    <img src="https://i.imgur.com/xAIAvWD.png" alt="Upload Image">
</p>
<p>The main page allows the user to upload an image containing a book page. The application then processes this image to extract the text and identify the book.</p>

<hr>

<h3>Processed Image and Results</h3>
<p align="center">
    <img src="https://i.imgur.com/bbSfVCY.png" alt="Results">
</p>
<p>After processing, the application displays the original image, the extracted text, and the best matching book information.</p>

