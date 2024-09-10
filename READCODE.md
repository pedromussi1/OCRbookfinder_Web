<h1>Code Breakdown</h1>

<p>The goal of this project was to develop a program that uses image recognition to identify comic books based on their covers. Built with Flask and a custom-trained machine learning model, the application allows users to upload an image of a comic book cover and receive identification results. The system processes and classifies the uploaded images, providing users with relevant information about the comic book. This tool can be particularly useful for comic book collectors, retailers, and enthusiasts.</p>

<h2>Preprocess.py</h2>

<p>This script is responsible for preprocessing and augmenting images from a dataset to enhance the model's ability to recognize comic book covers. Let's break down the functionality and purpose of the code:</p>

<h3>1. Imports and Utility Functions:</h3>
<ul>
  <li><code>cv2</code>: OpenCV is used for reading, manipulating, and saving images.</li>
  <li><code>os</code>: Provides functionalities to interact with the operating system, such as file path manipulations.</li>
  <li><code>numpy</code> (as <code>np</code>): Used for numerical operations, including creating random backgrounds.</li>
  <li><code>ImageDataGenerator</code> from <code>tensorflow.keras.preprocessing.image</code>: Facilitates image data augmentation to improve model generalization.</li>
  <li><code>replace_background</code> from <code>utils</code>: A utility function to replace the background of images, ensuring consistency across images by normalizing backgrounds.</li>
</ul>

<h3>2. <code>preprocess_images</code> Function:</h3>
<p>The core function of the script that handles preprocessing and augmenting the images.</p>

<ul>
  <li><b>Input Parameters:</b>
    <ul>
      <li><code>input_dir</code>: Directory containing the raw images.</li>
      <li><code>output_dir</code>: Directory where processed images will be saved.</li>
      <li><code>augment</code> (default=True): Boolean flag to indicate whether to perform image augmentation.</li>
    </ul>
  </li>

  <li><b>Function Workflow:</b>
    <ul>
      <li><b>Create Output Directory:</b> Checks if the output directory exists and creates it if necessary.</li>
      <li><b>Data Augmentation Setup:</b> Defines an <code>ImageDataGenerator</code> object with various augmentation transformations (rotation, shifts, shear, zoom, and flips).</li>
      <li><b>Processing Each Image:</b>
        <ul>
          <li>Iterates over each folder and image in the <code>input_dir</code>.</li>
          <li>Reads each image and optionally replaces its background with a randomly generated one using the <code>replace_background</code> function.</li>
          <li>Resizes the image to 224x224 pixels (a common input size for many deep learning models).</li>
          <li>Saves the processed image in the appropriate subdirectory within <code>output_dir</code>.</li>
          <li><b>Augmentation:</b> If augmentation is enabled, generates additional variations of the image using the specified transformations and saves them.</li>
        </ul>
      </li>
    </ul>
  </li>
</ul>

<h3>3. Main Execution Block:</h3>
<ul>
  <li>The script is designed to run as a standalone program.</li>
  <li>Calls the <code>preprocess_images</code> function with the <code>"dataset"</code> directory as the source of raw images and <code>"preprocessed_dataset"</code> as the destination for processed images.</li>
</ul>


<h3>Key Features:</h3>
<ul>
  <li><b>Background Replacement:</b> Normalizes image backgrounds to reduce noise and variability, which can improve model performance.</li>
  <li><b>Data Augmentation:</b> Generates multiple variations of each image, enhancing the diversity of the training set and improving model robustness.</li>
  <li><b>Image Resizing:</b> Ensures uniform input size for the model, which is crucial for deep learning applications.</li>
</ul>

<h3>Potential Improvements:</h3>
<ul>
  <li><b>Customizable Augmentation Parameters:</b> Allow users to specify augmentation parameters via function arguments.</li>
  <li><b>Background Replacement Control:</b> Make background replacement optional or allow users to provide custom backgrounds.</li>
  <li><b>Logging and Progress Indicators:</b> Implement logging to provide feedback on the number of images processed or any errors encountered.</li>
</ul>

<h3>Purpose and Benefits:</h3>
<p>The <code>preprocess.py</code> script is designed to prepare images for training a deep learning model. By resizing, normalizing backgrounds, and augmenting data, it enhances the dataset's quality, leading to a more robust and accurate comic book cover recognition model.</p>

<hr>

<h2>Model.py</h2>

<p>This script is designed to load a preprocessed dataset of comic book covers, build a deep learning model using transfer learning, and train it to classify comic books based on their covers. Below is a detailed breakdown of the code's functionality:</p>


<h3>1. Imports and Dependencies:</h3>
<ul>
  <li><code>numpy</code> (as <code>np</code>): For numerical operations and data manipulation.</li>
  <li><code>cv2</code>: OpenCV library used for image loading and resizing.</li>
  <li><code>MobileNetV2</code> from <code>tensorflow.keras.applications</code>: A pre-trained convolutional neural network used for transfer learning.</li>
  <li><code>Dense</code>, <code>GlobalAveragePooling2D</code> from <code>tensorflow.keras.layers</code>: Layers for building the neural network.</li>
  <li><code>Model</code> from <code>tensorflow.keras.models</code>: Used for creating a Keras model.</li>
  <li><code>ImageDataGenerator</code> from <code>tensorflow.keras.preprocessing.image</code>: For on-the-fly data augmentation.</li>
  <li><code>train_test_split</code> from <code>sklearn.model_selection</code>: Splits the dataset into training and validation sets.</li>
  <li><code>os</code>: For interacting with the file system.</li>
</ul>

<h3>2. <code>load_data</code> Function:</h3>
<p>This function loads the preprocessed images and their corresponding labels from the dataset directory.</p>

<ul>
  <li><b>Input:</b> <code>data_dir</code> - The directory where preprocessed images are stored.</li>
  <li><b>Process:</b>
    <ul>
      <li>Initializes empty lists <code>X</code> for images and <code>y</code> for labels.</li>
      <li>Iterates through each class label (subdirectory) in <code>data_dir</code>.</li>
      <li>Loads each image file, resizes it to 224x224 pixels, and appends it to <code>X</code>.</li>
      <li>Appends the corresponding label index to <code>y</code>.</li>
    </ul>
  </li>
  <li><b>Output:</b> Returns:
    <ul>
      <li><code>X</code>: Numpy array of normalized images.</li>
      <li><code>y</code>: Numpy array of labels.</li>
      <li><code>class_labels</code>: List of class names corresponding to each label index.</li>
    </ul>
  </li>
</ul>

<h3>3. <code>build_model</code> Function:</h3>
<p>This function constructs a deep learning model using transfer learning with MobileNetV2 as the base model.</p>

<ul>
  <li><b>Input:</b> <code>num_classes</code> - The number of unique comic book classes to be recognized.</li>
  <li><b>Process:</b>
    <ul>
      <li>Loads the MobileNetV2 model pre-trained on the ImageNet dataset without the top layers.</li>
      <li>Adds a global average pooling layer and a dense layer with 1024 neurons and ReLU activation.</li>
      <li>Adds an output layer with <code>num_classes</code> neurons and softmax activation for classification.</li>
      <li>Freezes all layers in the base model to retain learned weights.</li>
      <li>Compiles the model with Adam optimizer, sparse categorical cross-entropy loss, and accuracy metric.</li>
    </ul>
  </li>
  <li><b>Output:</b> Returns the compiled model ready for training.</li>
</ul>

<h3>4. <code>main</code> Function:</h3>
<p>The main function orchestrates the data loading, model building, and training process.</p>

<ul>
  <li><b>Data Preparation:</b> 
    <ul>
      <li>Loads preprocessed data from the <code>"preprocessed_dataset"</code> directory.</li>
      <li>Splits the data into training and validation sets using an 80/20 split.</li>
    </ul>
  </li>
  <li><b>Model Building:</b> Builds the model using the number of unique classes.</li>
  <li><b>Data Augmentation:</b> 
    <ul>
      <li>Initializes an <code>ImageDataGenerator</code> for augmenting the training data with random transformations (rotation, shift, zoom, flip).</li>
    </ul>
  </li>
  <li><b>Training:</b> 
    <ul>
      <li>Trains the model using the augmented data and evaluates it on the validation set.</li>
      <li>Runs for 10 epochs with a batch size of 32.</li>
    </ul>
  </li>
  <li><b>Model Saving:</b> Saves the trained model to a file named <code>"comic_model.h5"</code>.</li>
</ul>

<h3>Key Features:</h3>
<ul>
  <li><b>Transfer Learning:</b> Leverages the pre-trained MobileNetV2 model to reduce training time and improve performance by using previously learned features.</li>
  <li><b>Data Augmentation:</b> Enhances the diversity of the training data, which helps the model generalize better to unseen images.</li>
  <li><b>Efficient Training:</b> Freezes the base model layers, allowing only the new layers to be trained, which speeds up the training process and reduces overfitting.</li>
</ul>

<h3>Potential Improvements:</h3>
<ul>
  <li><b>Unfreeze Layers:</b> Fine-tune some of the deeper layers of the base model to adapt better to the specific dataset.</li>
  <li><b>Early Stopping:</b> Implement early stopping to prevent overfitting by monitoring the validation loss during training.</li>
  <li><b>Hyperparameter Tuning:</b> Experiment with different optimizers, learning rates, and model architectures for improved performance.</li>
</ul>

<h3>Purpose and Benefits:</h3>
<p>The <code>train_model.py</code> script serves as the core module for training a deep learning model to recognize comic book covers. It uses transfer learning with MobileNetV2 to achieve high accuracy with limited data and resources. The model is trained with augmented data, enhancing its ability to generalize to new comic book covers and providing a robust solution for comic book recognition.</p>

<hr>

<h2>Predict.py</h2>

<p>This script is designed to load a pre-trained deep learning model and a label encoder to predict the class of a comic book cover image. Below is a detailed breakdown of the code's functionality:</p>


<h3>1. Imports and Dependencies:</h3>
<ul>
  <li><code>numpy</code> (as <code>np</code>): For numerical operations and data manipulation.</li>
  <li><code>cv2</code>: OpenCV library for image loading and preprocessing.</li>
  <li><code>tensorflow</code> (as <code>tf</code>): To load the pre-trained Keras model.</li>
  <li><code>pickle</code>: For loading the label encoder used to map predicted labels back to class names.</li>
</ul>

<h3>2. <code>load_model_and_encoder</code> Function:</h3>
<p>This function loads the pre-trained deep learning model and the label encoder used for mapping numeric predictions to class labels.</p>

<ul>
  <li><b>Inputs:</b>
    <ul>
      <li><code>model_path</code>: The file path to the saved Keras model (<code>.h5</code> file).</li>
      <li><code>encoder_path</code>: The file path to the saved label encoder (<code>.pkl</code> file).</li>
    </ul>
  </li>
  <li><b>Process:</b>
    <ul>
      <li>Loads the model using <code>tf.keras.models.load_model()</code>.</li>
      <li>Loads the label encoder using <code>pickle.load()</code> from the provided file path.</li>
    </ul>
  </li>
  <li><b>Output:</b> Returns the loaded model and label encoder.</li>
</ul>

<h3>3. <code>preprocess_image</code> Function:</h3>
<p>This function loads an image and preprocesses it for prediction by the model.</p>

<ul>
  <li><b>Inputs:</b>
    <ul>
      <li><code>image_path</code>: The file path to the image to be classified.</li>
      <li><code>img_size</code>: The target size (width and height) to resize the image (should match the model's input size).</li>
    </ul>
  </li>
  <li><b>Process:</b>
    <ul>
      <li>Loads the image from the specified file path using OpenCV's <code>cv2.imread()</code>.</li>
      <li>Raises a <code>ValueError</code> if the image could not be loaded.</li>
      <li>Resizes the image to the specified <code>img_size</code> using <code>cv2.resize()</code>.</li>
      <li>Normalizes the image pixel values to the range [0, 1] by dividing by 255.0.</li>
      <li>Adds a batch dimension to the image array using <code>np.expand_dims()</code> to make it compatible with the model's expected input shape.</li>
    </ul>
  </li>
  <li><b>Output:</b> Returns the preprocessed image ready for prediction.</li>
</ul>

<h3>4. <code>predict_class</code> Function:</h3>
<p>This function uses the loaded model to predict the class of the preprocessed image.</p>

<ul>
  <li><b>Inputs:</b>
    <ul>
      <li><code>model</code>: The pre-trained Keras model.</li>
      <li><code>img</code>: The preprocessed image array.</li>
      <li><code>label_encoder</code>: The label encoder used to map numeric predictions to class labels.</li>
    </ul>
  </li>
  <li><b>Process:</b>
    <ul>
      <li>Uses the model's <code>predict()</code> method to get class probabilities for the input image.</li>
      <li>Finds the index of the highest predicted probability using <code>np.argmax()</code>.</li>
      <li>Maps the predicted class index back to the corresponding label using the label encoder's <code>inverse_transform()</code> method.</li>
    </ul>
  </li>
  <li><b>Output:</b> Returns the predicted class label as a string.</li>
</ul>

<h3>5. <code>main</code> Function:</h3>
<p>The main function coordinates the overall process of loading the model, preprocessing the image, and predicting the comic book class.</p>

<ul>
  <li><b>Variables:</b>
    <ul>
      <li><code>model_path</code>: File path to the saved Keras model (<code>'comic_book_classifier_model.h5'</code>).</li>
      <li><code>encoder_path</code>: File path to the saved label encoder (<code>'label_encoder.pkl'</code>).</li>
      <li><code>img_path</code>: File path to the image of the comic book cover to be classified (user must replace with actual image path).</li>
    </ul>
  </li>
  <li><b>Process:</b>
    <ul>
      <li>Loads the model and label encoder using the <code>load_model_and_encoder()</code> function.</li>
      <li>Preprocesses the image using the <code>preprocess_image()</code> function.</li>
      <li>Predicts the comic book class using the <code>predict_class()</code> function.</li>
      <li>Prints the predicted class label to the console.</li>
    </ul>
  </li>
</ul>

<h3>Key Features:</h3>
<ul>
  <li><b>Model Loading:</b> Efficiently loads a pre-trained model and label encoder for classification.</li>
  <li><b>Image Preprocessing:</b> Ensures the input image is correctly formatted and normalized for the model.</li>
  <li><b>Prediction and Decoding:</b> Accurately predicts the class of a comic book cover and converts the predicted class index back to a human-readable label.</li>
</ul>

<h3>Potential Improvements:</h3>
<ul>
  <li><b>Exception Handling:</b> Enhance error handling to cover additional scenarios, such as missing files or invalid model formats.</li>
  <li><b>Batch Prediction:</b> Modify the script to handle multiple images at once for batch processing and prediction.</li>
  <li><b>Model Optimization:</b> Use techniques such as model quantization or pruning to improve prediction speed and reduce model size.</li>
</ul>

<h3>Purpose and Benefits:</h3>
<p>The <code>predict_model.py</code> script provides a simple and effective way to classify comic book covers using a pre-trained deep learning model. This can be useful for comic book collectors, retailers, or libraries to automate the organization and identification of comic books.</p>

<hr>

<h2>app.py</h2>

<p>This Flask application is designed to classify comic book covers by allowing users to upload an image, which is then processed and predicted using a pre-trained deep learning model. The prediction is displayed to the user in the form of a label.</p>

<h3>1. Imports and Dependencies:</h3>
<ul>
  <li><code>os</code>: Provides functions to interact with the operating system, such as creating directories.</li>
  <li><code>flask</code> (from <code>Flask</code>, <code>render_template</code>, <code>request</code>, <code>redirect</code>, <code>url_for</code>): The core components of the Flask web framework to handle web server functionality.</li>
  <li><code>tensorflow.keras.models</code> (as <code>load_model</code>): For loading the pre-trained Keras model.</li>
  <li><code>cv2</code>: OpenCV library for image loading and preprocessing.</li>
  <li><code>numpy</code> (as <code>np</code>): For numerical operations and data manipulation.</li>
</ul>

<h3>2. Model Loading and Class Labels:</h3>
<p>The pre-trained model and the list of class labels are loaded at the start of the script:</p>
<ul>
  <li><code>model = load_model('comic_book_classifier_model.h5')</code>: Loads the pre-trained Keras model from the specified file path.</li>
  <li><code>class_labels</code>: A list of labels representing different comic book classes that the model can predict. These labels should match the classes the model was trained on.</li>
</ul>

<h3>3. <code>preprocess_image</code> Function:</h3>
<p>This function preprocesses the uploaded image to ensure compatibility with the input shape expected by the model:</p>

<ul>
  <li><b>Inputs:</b> 
    <ul>
      <li><code>image_path</code>: The file path to the uploaded image to be processed.</li>
    </ul>
  </li>
  <li><b>Process:</b>
    <ul>
      <li>Loads the image using OpenCV's <code>cv2.imread()</code>.</li>
      <li>Resizes the image to the target size (224x224) using <code>cv2.resize()</code>.</li>
      <li>Normalizes pixel values to the range [0, 1] by converting to <code>float32</code> and dividing by 255.0.</li>
      <li>Adds a batch dimension to the image array using <code>np.expand_dims()</code> to match the input shape required by the model (1, 224, 224, 3).</li>
    </ul>
  </li>
  <li><b>Output:</b> Returns the preprocessed image ready for prediction.</li>
</ul>

<h3>4. File Upload and Storage Configuration:</h3>
<p>The application defines an upload folder for storing images temporarily:</p>
<ul>
  <li><code>UPLOAD_FOLDER</code>: Specifies the folder (<code>uploads</code>) to store uploaded images.</li>
  <li><code>os.makedirs(UPLOAD_FOLDER)</code>: Creates the upload directory if it does not already exist.</li>
</ul>

<h3>5. <code>index</code> Route:</h3>
<p>The main route (<code>/</code>) serves both the home page for file upload and handles the file upload process:</p>

<ul>
  <li><b>Methods:</b> Supports both GET and POST methods:
    <ul>
      <li><code>GET</code>: Renders the home page (<code>index.html</code>), where users can upload an image.</li>
      <li><code>POST</code>: Handles the file upload, preprocessing, and prediction:
        <ul>
          <li>Checks if a file is uploaded and handles cases where no file is selected.</li>
          <li>Saves the uploaded file to the specified <code>UPLOAD_FOLDER</code>.</li>
          <li>Calls <code>preprocess_image()</code> to prepare the image for the model.</li>
          <li>Makes a prediction using the model's <code>predict()</code> method.</li>
          <li>Determines the predicted class label by finding the maximum predicted probability and maps it to the corresponding label in <code>class_labels</code>.</li>
          <li>Renders the result page (<code>result.html</code>) with the predicted class label.</li>
        </ul>
      </li>
    </ul>
  </li>
</ul>

<h3>6. Application Run Configuration:</h3>
<p>The script starts the Flask application in debug mode if run directly:</p>
<ul>
  <li><code>app.run(debug=True)</code>: Runs the application with debugging enabled to provide detailed error messages during development.</li>
</ul>

<h3>Key Features:</h3>
<ul>
  <li><b>Image Upload:</b> Allows users to upload an image of a comic book cover directly from the web interface.</li>
  <li><b>Real-time Prediction:</b> Classifies the uploaded image using a deep learning model and provides immediate feedback to the user.</li>
  <li><b>Dynamic Content:</b> Utilizes Flask's templating engine to dynamically display prediction results.</li>
</ul>

<h3>Potential Improvements:</h3>
<ul>
  <li><b>Enhance Error Handling:</b> Add more robust error handling for scenarios such as unsupported file types, missing files, or corrupted images.</li>
  <li><b>Improve User Interface:</b> Create a more user-friendly front-end with enhanced design and clear instructions for uploading images.</li>
  <li><b>Optimize Model Performance:</b> Consider optimizing the model for faster predictions, especially for larger image sizes or complex models.</li>
  <li><b>Implement Security Measures:</b> Include file validation and security checks to prevent malicious file uploads.</li>
</ul>

<h3>Purpose and Benefits:</h3>
<p>This Flask application offers a convenient way to classify comic book covers using a pre-trained deep learning model. It serves as a valuable tool for comic book collectors, retailers, or libraries to automate the organization and identification of comic books.</p>
