# 🍛 Bangladeshi Food Classifier API

FastAPI backend for the food classification model, designed to work with Flutter and other mobile apps.

## 📁 Setup

### 1. Copy Required Files
Copy these files from the `app` folder to `backend`:
```bash
cp ../app/model.pth .
cp ../app/class_names.json .
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Locally
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at: `http://localhost:8000`

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info and available endpoints |
| GET | `/health` | Health check |
| GET | `/classes` | List all food classes |
| POST | `/predict` | Predict food from image file |
| POST | `/predict/base64` | Predict food from base64 image |

## 🧪 Test the API

### Using cURL
```bash
# Health check
curl http://localhost:8000/health

# Predict from file
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_food_image.jpg"
```

### Using Python
```python
import requests

# Upload image file
with open("food.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/predict",
        files={"file": f}
    )
print(response.json())
```

## 🚀 Deployment Options

### Option 1: Railway (Recommended - Free tier available)
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway auto-detects the Dockerfile
6. Your API URL will be: `https://your-app.railway.app`

### Option 2: Render (Free tier available)
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. New → Web Service
4. Connect your repository
5. Settings:
   - Runtime: Docker
   - Free instance type
6. Your API URL will be: `https://your-app.onrender.com`

### Option 3: Google Cloud Run
```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT/food-classifier

# Deploy
gcloud run deploy food-classifier \
  --image gcr.io/YOUR_PROJECT/food-classifier \
  --platform managed \
  --allow-unauthenticated
```

### Option 4: Heroku
```bash
heroku create your-food-classifier
heroku container:push web
heroku container:release web
```

## 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| PORT | Server port | 8000 |

## 📱 Flutter Integration

```dart
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

class FoodClassifierApi {
  static const String baseUrl = "https://your-api-url.com";

  static Future<Map<String, dynamic>> predictFood(File imageFile) async {
    var request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/predict'),
    );
    request.files.add(
      await http.MultipartFile.fromPath('file', imageFile.path),
    );
    
    var response = await request.send();
    var responseBody = await response.stream.bytesToString();
    return json.decode(responseBody);
  }
}
```

## 📄 Response Format

```json
{
  "success": true,
  "prediction": {
    "class": "Biryani",
    "confidence": 0.95,
    "confidence_percent": "95.0%"
  },
  "top5": [
    {"class": "Biryani", "confidence": 0.95},
    {"class": "Pulao", "confidence": 0.03},
    ...
  ]
}
```
