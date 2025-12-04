# 🍛 Bangladeshi Food Classifier App

AI-powered food image classification with nutrition suggestions.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd app
pip install -r requirements.txt
```

### 2. Run the App
```bash
streamlit run food_classifier_app.py
```

### 3. Upload Your Model
1. Open the app in browser (usually http://localhost:8501)
2. In the sidebar, upload:
   - `best_model_*.pth` (your trained model)
   - `class_names.json` (class names file)
3. Upload a food image to classify!

## 📁 Files from Colab Training

After training, you downloaded `food_classification_models.zip` containing:
- `best_model_ResNet50.pth` (or whichever model performed best)
- `class_names.json`
- `training_summary.json`
- Individual model files for all 5 models

## 🌐 Deploy Online (Free Options)

### Option 1: Streamlit Cloud (Easiest)
1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Deploy!

### Option 2: Hugging Face Spaces
1. Create account at [huggingface.co](https://huggingface.co)
2. Create new Space (Streamlit SDK)
3. Upload your files
4. Free GPU available!

### Option 3: Render.com
1. Push to GitHub
2. Connect to Render
3. Deploy as web service

## 📱 Mobile App Options

### Gradio (Quick Demo)
```python
import gradio as gr
# Similar interface, works on mobile browsers
```

### Flutter/React Native
- Export model to ONNX format
- Use TensorFlow Lite for mobile
- Build native mobile app

## 📊 Features

- ✅ Food image classification
- ✅ Confidence scores
- ✅ Top 3 predictions
- ✅ Nutrition facts (calories, protein, carbs, fat)
- ✅ Health tips for each food
- ✅ 33 Bangladeshi food classes

## 🍽️ Supported Foods

The model can recognize 33 types of Bangladeshi foods including:
- Biryani, Kacchi Biryani
- Chicken Curry, Fish Curry
- Dal, Khichuri
- Hilsha Fish
- Jalebi, Rasmalai, Kheer
- And many more!

## 📝 License

For academic/thesis use.
