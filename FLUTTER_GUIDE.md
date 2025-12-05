# 🚀 Complete Step-by-Step Guide: FastAPI + Flutter Food Classifier

## Overview
This guide will help you:
1. Deploy your FastAPI backend online (FREE)
2. Create a Flutter app that uses the API

---

# PART 1: Deploy FastAPI Backend (FREE)

## Option A: Deploy on Render.com (Recommended - Easiest)

### Step 1: Create GitHub Repository (if not done)
Your code is already on GitHub at: `https://github.com/MasudBinMazid/Local-Food-Classifier`

Push the backend folder:
```powershell
cd g:\Food\Code
git add backend/
git commit -m "Add FastAPI backend for mobile app"
git push
```

### Step 2: Sign Up on Render
1. Go to **https://render.com**
2. Click **"Get Started for Free"**
3. Sign up with **GitHub** (recommended)

### Step 3: Create Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository: `MasudBinMazid/Local-Food-Classifier`
3. Configure:
   - **Name**: `food-classifier-api`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Docker`
   - **Instance Type**: `Free`

4. Click **"Create Web Service"**

5. Wait 5-10 minutes for deployment

6. Your API URL will be: `https://food-classifier-api.onrender.com`

---

## Option B: Deploy on Railway.app

### Step 1: Sign Up
1. Go to **https://railway.app**
2. Click **"Login"** → **"Login with GitHub"**

### Step 2: Deploy
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repository
4. Click on the service → **"Settings"**
5. Set **Root Directory**: `backend`
6. Railway auto-detects Dockerfile
7. Click **"Deploy"**

8. Your API URL will be: `https://your-app.up.railway.app`

---

## Option C: Deploy on PythonAnywhere (Free)

### Step 1: Sign Up
1. Go to **https://www.pythonanywhere.com**
2. Click **"Pricing & signup"** → **"Create a Beginner account"**

### Step 2: Upload Files
1. Go to **"Files"** tab
2. Create folder: `food_classifier`
3. Upload: `main.py`, `model.pth`, `class_names.json`, `requirements.txt`

### Step 3: Setup Virtual Environment
1. Go to **"Consoles"** → **"Bash"**
2. Run:
```bash
mkvirtualenv --python=/usr/bin/python3.10 foodenv
pip install -r food_classifier/requirements.txt
```

### Step 4: Create Web App
1. Go to **"Web"** tab
2. Click **"Add a new web app"**
3. Choose **"Manual configuration"** → **Python 3.10**
4. Set virtualenv: `/home/yourusername/.virtualenvs/foodenv`

### Step 5: Configure WSGI
Edit the WSGI file:
```python
import sys
path = '/home/yourusername/food_classifier'
if path not in sys.path:
    sys.path.append(path)

from main import app
```

---

# PART 2: Create Flutter App

## Step 1: Install Flutter
1. Download Flutter from: **https://docs.flutter.dev/get-started/install/windows**
2. Extract to `C:\flutter`
3. Add `C:\flutter\bin` to PATH
4. Open new terminal and run:
```powershell
flutter doctor
```

## Step 2: Install Android Studio
1. Download from: **https://developer.android.com/studio**
2. Install with default settings
3. Open Android Studio → SDK Manager → Install Android SDK

## Step 3: Create Flutter Project
```powershell
cd g:\Food\Code
flutter create flutter_food_app
cd flutter_food_app
```

## Step 4: Add Dependencies
Open `pubspec.yaml` and add:
```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  image_picker: ^1.0.4
  permission_handler: ^11.0.1
```

Run:
```powershell
flutter pub get
```

## Step 5: Create the App Files

### lib/main.dart
```dart
import 'package:flutter/material.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(const FoodClassifierApp());
}

class FoodClassifierApp extends StatelessWidget {
  const FoodClassifierApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Food Classifier',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.orange,
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}
```

### lib/screens/home_screen.dart
```dart
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../services/api_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  File? _image;
  Map<String, dynamic>? _prediction;
  bool _isLoading = false;
  String? _error;

  final ImagePicker _picker = ImagePicker();

  Future<void> _pickImage(ImageSource source) async {
    try {
      final XFile? pickedFile = await _picker.pickImage(
        source: source,
        maxWidth: 1024,
        maxHeight: 1024,
        imageQuality: 85,
      );

      if (pickedFile != null) {
        setState(() {
          _image = File(pickedFile.path);
          _prediction = null;
          _error = null;
        });
        await _classifyImage();
      }
    } catch (e) {
      setState(() => _error = 'Failed to pick image: $e');
    }
  }

  Future<void> _classifyImage() async {
    if (_image == null) return;

    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final result = await ApiService.predictFood(_image!);
      setState(() {
        _prediction = result;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = 'Prediction failed: $e';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('🍛 Food Classifier'),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Image Preview
            Container(
              height: 300,
              decoration: BoxDecoration(
                color: Colors.grey[800],
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.grey[600]!),
              ),
              child: _image != null
                  ? ClipRRect(
                      borderRadius: BorderRadius.circular(16),
                      child: Image.file(_image!, fit: BoxFit.cover),
                    )
                  : const Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.restaurant, size: 64, color: Colors.grey),
                          SizedBox(height: 16),
                          Text('Select or capture a food image',
                              style: TextStyle(color: Colors.grey)),
                        ],
                      ),
                    ),
            ),
            const SizedBox(height: 20),

            // Buttons
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => _pickImage(ImageSource.camera),
                    icon: const Icon(Icons.camera_alt),
                    label: const Text('Camera'),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => _pickImage(ImageSource.gallery),
                    icon: const Icon(Icons.photo_library),
                    label: const Text('Gallery'),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),

            // Loading indicator
            if (_isLoading)
              const Center(
                child: Column(
                  children: [
                    CircularProgressIndicator(),
                    SizedBox(height: 16),
                    Text('Analyzing food...'),
                  ],
                ),
              ),

            // Error message
            if (_error != null)
              Card(
                color: Colors.red[900],
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Text(_error!, style: const TextStyle(color: Colors.white)),
                ),
              ),

            // Prediction result
            if (_prediction != null && _prediction!['success'] == true) ...[
              Card(
                color: Colors.green[800],
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    children: [
                      const Text('Detected Food:',
                          style: TextStyle(fontSize: 16)),
                      const SizedBox(height: 8),
                      Text(
                        _prediction!['prediction']['class'],
                        style: const TextStyle(
                          fontSize: 28,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Confidence: ${_prediction!['prediction']['confidence_percent']}',
                        style: const TextStyle(fontSize: 18),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              
              // Top 5 predictions
              const Text('Other possibilities:',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              ...(_prediction!['top5'] as List).skip(1).map((item) => ListTile(
                    title: Text(item['class']),
                    trailing: Text(
                      '${(item['confidence'] * 100).toStringAsFixed(1)}%',
                    ),
                  )),
            ],
          ],
        ),
      ),
    );
  }
}
```

### lib/services/api_service.dart
```dart
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

class ApiService {
  // 🔴 CHANGE THIS TO YOUR DEPLOYED API URL
  static const String baseUrl = "https://food-classifier-api.onrender.com";
  // For local testing: "http://10.0.2.2:8000" (Android emulator)
  // For local testing: "http://localhost:8000" (iOS simulator)

  static Future<Map<String, dynamic>> predictFood(File imageFile) async {
    try {
      var uri = Uri.parse('$baseUrl/predict');
      var request = http.MultipartRequest('POST', uri);
      
      request.files.add(
        await http.MultipartFile.fromPath('file', imageFile.path),
      );

      var streamedResponse = await request.send().timeout(
        const Duration(seconds: 30),
      );
      
      var response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Server error: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  static Future<List<String>> getClasses() async {
    try {
      var response = await http.get(Uri.parse('$baseUrl/classes'));
      if (response.statusCode == 200) {
        var data = json.decode(response.body);
        return List<String>.from(data['classes']);
      } else {
        throw Exception('Failed to load classes');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }
}
```

## Step 6: Configure Android Permissions

### android/app/src/main/AndroidManifest.xml
Add before `<application>`:
```xml
<uses-permission android:name="android.permission.INTERNET"/>
<uses-permission android:name="android.permission.CAMERA"/>
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"/>
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>
```

Add inside `<application>`:
```xml
android:usesCleartextTraffic="true"
```

## Step 7: Run the App
```powershell
flutter run
```

---

# PART 3: Testing

## Test API Locally First
```powershell
cd g:\Food\Code\backend
& g:\Food\Code\.venv\Scripts\Activate.ps1
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Then open: http://localhost:8000/docs (Swagger UI to test)

## Test with cURL
```powershell
curl -X POST "http://localhost:8000/predict" -F "file=@test_image.jpg"
```

---

# Summary Checklist

- [ ] Push backend to GitHub
- [ ] Deploy on Render.com (or Railway)
- [ ] Get your API URL
- [ ] Install Flutter
- [ ] Create Flutter project
- [ ] Update API URL in `api_service.dart`
- [ ] Run the app!

---

# Troubleshooting

## "Connection refused" error
- Check if API is running
- Check API URL is correct
- For Android emulator, use `10.0.2.2` instead of `localhost`

## "Model not loading" on Render
- Make sure `model.pth` is in the `backend` folder
- Check if file is uploaded to GitHub (not in .gitignore)

## Free tier sleeps
- Render/Railway free tier sleeps after inactivity
- First request takes 30-60 seconds to wake up
