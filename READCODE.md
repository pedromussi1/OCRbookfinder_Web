<h1>Code Breakdown</h1>

<p>The Emotion Detector from Voice project is an AI-powered application designed to classify human emotions from voice recordings. The system extracts audio features such as MFCCs, chroma, mel spectrograms, spectral contrast, and tonnetz from `.wav` files. It uses machine learning models (Random Forest or MLPClassifier) to predict emotions like happy, sad, angry, neutral, and more. Users can upload a voice recording through a Streamlit interface to see the detected emotion and its probability distribution.</p>

<h2>Audio Feature Extraction and Model Training (train_model.py)</h2>

<p>The <b>train_model.py</b> file handles dataset loading, feature extraction, model training, and saving the trained model. The process includes:</p>

<p>Loading Audio: Each `.wav` file in the dataset is read using librosa.</p>

<p>Feature Extraction: MFCCs, chroma, mel spectrogram, spectral contrast, and tonnetz features are extracted and concatenated into a single feature vector.</p> 

<p>Training the Model: A RandomForestClassifier is trained on the extracted features to predict emotion labels.</p> 

<p>Saving the Model: The trained model is saved as <code>model.pkl</code> for later use in emotion detection.</p>

```py

def extract_features(file_path):
    X, sample_rate = librosa.load(file_path, res_type='kaiser_fast')
    mfccs = np.mean(librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=40).T, axis=0)
    chroma = np.mean(librosa.feature.chroma_stft(y=X, sr=sample_rate).T, axis=0)
    mel = np.mean(librosa.feature.melspectrogram(y=X, sr=sample_rate).T, axis=0)
    contrast = np.mean(librosa.feature.spectral_contrast(y=X, sr=sample_rate).T, axis=0)
    tonnetz = np.mean(librosa.feature.tonnetz(y=librosa.effects.harmonic(X), sr=sample_rate).T, axis=0)
    return np.hstack([mfccs, chroma, mel, contrast, tonnetz])

def train_and_save_model(dataset_path, model_output_path="model.pkl"):
    X, y = load_data(dataset_path)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)
    joblib.dump(model, model_output_path)

```

<h2>Dataset Processing and Training (emotion_detect.py)</h2> 

<p>The <b>emotion_detect.py</b> script provides a more flexible training pipeline using an MLPClassifier. It also supports selective emotion categories and evaluates model performance in detail.</p> 

<p>Loading Dataset: Recursively reads `.wav` files and maps file name codes to emotion labels.</p> 

<p>Feature Extraction: MFCC, chroma, and mel spectrogram features are extracted.</p> 

<p>Model Training: An MLPClassifier is trained to predict emotions from audio features.</p> 

<p>Evaluation: Prints accuracy, classification report, and confusion matrix.</p> 

<p>Model Saving: Saves the trained model to <code>model.pkl</code> using joblib.</p>

```py

def extract_features(file_path, mfcc=True, chroma=True, mel=True):
    X, sample_rate = librosa.load(file_path, sr=None)
    result = np.array([])
    if mfcc:
        result = np.hstack((result, np.mean(librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=40).T, axis=0)))
    if chroma:
        stft = np.abs(librosa.stft(X))
        result = np.hstack((result, np.mean(librosa.feature.chroma_stft(S=stft, sr=sample_rate).T, axis=0)))
    if mel:
        result = np.hstack((result, np.mean(librosa.feature.melspectrogram(y=X, sr=sample_rate).T, axis=0)))
    return result

model = MLPClassifier(hidden_layer_sizes=(300,), learning_rate='adaptive', max_iter=500)
model.fit(X_train, y_train)
joblib.dump(model, "model.pkl")

```

<h2>Streamlit Web Application (emotion_app.py)</h2> 

<p>The <b>emotion_app.py</b> file provides a user-friendly web interface using Streamlit. Users upload `.wav` audio files to detect emotions. The process involves:</p> 

<p>File Upload: Users upload their audio recording.</p> 

<p>Feature Extraction: The same MFCC, chroma, and mel features used during training are extracted.</p> 

<p>Emotion Prediction: The trained model predicts the most likely emotion and calculates probabilities for all possible emotions.</p> 

<p>Visualization: The predicted emotion and probability distribution are displayed using a bar chart.</p>

```py

def predict_emotion(file_path):
    features = extract_features(file_path).reshape(1, -1)
    prediction = model.predict(features)[0]
    probabilities = model.predict_proba(features)[0]
    prob_dict = {label: prob for label, prob in zip(model.classes_, probabilities)}
    return prediction, prob_dict

uploaded_file = st.file_uploader("Upload your audio file", type=["wav"])
if uploaded_file is not None:
    st.audio(uploaded_file, format="audio/wav")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(uploaded_file.read())
        temp_path = tmp.name
    prediction, prob_dict = predict_emotion(temp_path)
    st.success(f"Detected Emotion: **{prediction.upper()}** 🎯")
    st.bar_chart(pd.DataFrame(prob_dict, index=[0]).T.rename(columns={0: "Probability"}))

```

<h2>Deployment of Emotion Detector Application</h2> 

<h3>Dockerfile</h3> 

<p>The Dockerfile sets up the environment for running the Streamlit application:</p> 

<pre><code> FROM python:3.10-slim RUN apt-get update && apt-get install -y ffmpeg libsndfile1 && rm -rf /var/lib/apt/lists/* WORKDIR /app COPY requirements.txt . RUN pip install --no-cache-dir -r requirements.txt COPY . . EXPOSE 8501 CMD ["streamlit", "run", "emotion_app.py"] </code></pre> <h3>Fly.io Configuration (fly.toml)</h3> <pre><code> app = 'emotion-detector' primary_region = 'dfw' [build] [http_service] internal_port = 8501 force_https = true auto_stop_machines = 'stop' auto_start_machines = true min_machines_running = 0 processes = ['app'] [[vm]] memory = '2gb' cpu_kind = 'shared' cpus = 1 </code></pre>

<h2>Conclusion</h2> <p>This application combines audio signal processing, feature extraction, machine learning, and a web interface to detect human emotions from voice recordings. It demonstrates a complete end-to-end workflow from dataset preparation and model training to real-time prediction and visualization using Streamlit.</p> <div style="display: flex; justify-content: center; align-items: center;"> <img src="https://i.imgur.com/QrOq6sO.gif" alt="Voice Analysis" style="width: auto; height: 300px; margin: 20px;"> <img src="https://i.imgur.com/ENo2Dxd.png" alt="Emotion Detection UI" style="width: auto; height: 300px; margin: 20px;"> </div>
