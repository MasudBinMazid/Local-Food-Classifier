"""
FastAPI Backend for Bangladeshi Food Classifier
This API serves the food classification model for mobile apps (Flutter, React Native, etc.)

To run locally: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import io
import json
import os

# Initialize FastAPI app
app = FastAPI(
    title="Bangladeshi Food Classifier API",
    description="API for classifying Bangladeshi food images using deep learning",
    version="1.0.0"
)

# Enable CORS for Flutter/mobile apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (configure for production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for model and class names
model = None
class_names = None
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Image transformation pipeline
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


def detect_model_architecture(state_dict):
    """Detect model architecture from state dict keys"""
    keys = list(state_dict.keys())
    keys_str = ' '.join(keys)
    
    # Check for EfficientNet (features-based architecture with blocks)
    if 'features.0.0.weight' in keys and 'block' in keys_str:
        # EfficientNet B3 has more blocks than B0
        if any('features.7' in k for k in keys):
            return "EfficientNet-B3"
        return "EfficientNet-B0"
    
    if any('efficientnet' in k.lower() for k in keys):
        if any('_blocks.15' in k for k in keys):
            return "EfficientNet-B3"
        return "EfficientNet-B0"
    
    if any('denseblock' in k for k in keys):
        return "DenseNet-121"
    
    if any('layer1' in k for k in keys):
        return "ResNet-50" if any('conv3' in k for k in keys) else "ResNet-18"
    
    return "Unknown"


def load_model_and_classes():
    """Load the trained model and class names"""
    global model, class_names
    
    # Paths - adjust based on your deployment
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, "model.pth")
    class_names_path = os.path.join(script_dir, "class_names.json")
    
    # Fallback to app directory if not found in backend
    if not os.path.exists(model_path):
        model_path = os.path.join(script_dir, "..", "app", "model.pth")
        class_names_path = os.path.join(script_dir, "..", "app", "class_names.json")
    
    # Load class names
    with open(class_names_path, 'r') as f:
        class_dict = json.load(f)
    class_names = [class_dict[str(i)] for i in range(len(class_dict))]
    num_classes = len(class_names)
    
    # Load model state dict and detect architecture
    state_dict = torch.load(model_path, map_location=device)
    detected_arch = detect_model_architecture(state_dict)
    
    # Create model based on detected architecture
    if "ResNet-18" in detected_arch:
        model = models.resnet18(weights=None)
        model.fc = nn.Linear(model.fc.in_features, num_classes)
    elif "ResNet-50" in detected_arch:
        model = models.resnet50(weights=None)
        model.fc = nn.Linear(model.fc.in_features, num_classes)
    elif "EfficientNet-B0" in detected_arch:
        model = models.efficientnet_b0(weights=None)
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    elif "EfficientNet-B3" in detected_arch:
        model = models.efficientnet_b3(weights=None)
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    elif "DenseNet" in detected_arch:
        model = models.densenet121(weights=None)
        model.classifier = nn.Linear(model.classifier.in_features, num_classes)
    else:
        raise ValueError(f"Unknown architecture: {detected_arch}")
    
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()
    
    print(f"✅ Model loaded: {detected_arch}")
    print(f"✅ Classes: {num_classes}")
    print(f"✅ Device: {device}")


@app.on_event("startup")
async def startup_event():
    """Load model when server starts"""
    load_model_and_classes()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "message": "Bangladeshi Food Classifier API",
        "version": "1.0.0",
        "endpoints": {
            "predict": "/predict",
            "classes": "/classes",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check for monitoring"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "num_classes": len(class_names) if class_names else 0
    }


@app.get("/classes")
async def get_classes():
    """Get list of all food classes"""
    if class_names is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    return {
        "classes": class_names,
        "count": len(class_names)
    }


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """
    Predict food class from uploaded image
    
    - **file**: Image file (JPEG, PNG, etc.)
    
    Returns predicted class and confidence score
    """
    if model is None or class_names is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read and process image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        
        # Transform image
        input_tensor = transform(image).unsqueeze(0).to(device)
        
        # Predict
        with torch.no_grad():
            outputs = model(input_tensor)
            probabilities = torch.softmax(outputs, dim=1)
            confidence, predicted_idx = torch.max(probabilities, 1)
        
        predicted_class = class_names[predicted_idx.item()]
        confidence_score = float(confidence.item())
        
        # Get top 5 predictions
        top5_probs, top5_indices = torch.topk(probabilities, min(5, len(class_names)))
        top5_predictions = [
            {
                "class": class_names[idx.item()],
                "confidence": float(prob.item())
            }
            for prob, idx in zip(top5_probs[0], top5_indices[0])
        ]
        
        return JSONResponse(content={
            "success": True,
            "prediction": {
                "class": predicted_class,
                "confidence": confidence_score,
                "confidence_percent": f"{confidence_score * 100:.1f}%"
            },
            "top5": top5_predictions
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict/base64")
async def predict_base64(data: dict):
    """
    Predict food class from base64 encoded image
    Useful for Flutter apps that send base64 strings
    
    - **data**: JSON with "image" key containing base64 string
    """
    import base64
    
    if model is None or class_names is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    if "image" not in data:
        raise HTTPException(status_code=400, detail="Missing 'image' field")
    
    try:
        # Decode base64 image
        image_data = base64.b64decode(data["image"])
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        
        # Transform image
        input_tensor = transform(image).unsqueeze(0).to(device)
        
        # Predict
        with torch.no_grad():
            outputs = model(input_tensor)
            probabilities = torch.softmax(outputs, dim=1)
            confidence, predicted_idx = torch.max(probabilities, 1)
        
        predicted_class = class_names[predicted_idx.item()]
        confidence_score = float(confidence.item())
        
        return JSONResponse(content={
            "success": True,
            "prediction": {
                "class": predicted_class,
                "confidence": confidence_score,
                "confidence_percent": f"{confidence_score * 100:.1f}%"
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
