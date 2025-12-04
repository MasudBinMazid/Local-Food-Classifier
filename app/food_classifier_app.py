"""
🍛 Bangladeshi Food Classifier & Nutrition Advisor
A Streamlit app for food image classification with nutrition suggestions

To run: streamlit run food_classifier_app.py
"""

import streamlit as st
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import json
import os

# Page config
st.set_page_config(
    page_title="🍛 Bangladeshi Food Classifier",
    page_icon="🍛",
    layout="wide"
)

# ============================================
# NUTRITION DATABASE (per 100g serving)
# ============================================
NUTRITION_DATA = {
    "biryani": {
        "calories": 290,
        "protein": 12,
        "carbs": 35,
        "fat": 12,
        "fiber": 1.5,
        "description": "Aromatic rice dish with spices and meat",
        "health_tips": "High in carbs and protein. Good post-workout meal. Watch portion size due to oil content."
    },
    "bhuna_khichuri": {
        "calories": 180,
        "protein": 6,
        "carbs": 28,
        "fat": 5,
        "fiber": 3,
        "description": "Rice and lentil comfort food",
        "health_tips": "Good source of plant protein. Complete amino acid profile when rice and lentils combine."
    },
    "chapati": {
        "calories": 120,
        "protein": 4,
        "carbs": 25,
        "fat": 1,
        "fiber": 2,
        "description": "Whole wheat flatbread",
        "health_tips": "Low fat, good fiber content. Better alternative to white rice for diabetics."
    },
    "chicken_curry": {
        "calories": 180,
        "protein": 18,
        "carbs": 8,
        "fat": 10,
        "fiber": 1,
        "description": "Traditional chicken curry with spices",
        "health_tips": "High protein, good for muscle building. Choose skinless chicken for lower fat."
    },
    "dal": {
        "calories": 120,
        "protein": 8,
        "carbs": 20,
        "fat": 2,
        "fiber": 4,
        "description": "Lentil soup - protein powerhouse",
        "health_tips": "Excellent plant protein source. High fiber aids digestion. Low fat and heart-healthy."
    },
    "egg_curry": {
        "calories": 150,
        "protein": 10,
        "carbs": 5,
        "fat": 11,
        "fiber": 1,
        "description": "Boiled eggs in spiced curry",
        "health_tips": "Good protein and vitamin B12. Eggs provide complete protein with all amino acids."
    },
    "fish_curry": {
        "calories": 140,
        "protein": 16,
        "carbs": 6,
        "fat": 6,
        "fiber": 0.5,
        "description": "Fish cooked in traditional curry",
        "health_tips": "Omega-3 rich, great for heart and brain health. Choose small fish for more calcium."
    },
    "fried_rice": {
        "calories": 250,
        "protein": 8,
        "carbs": 35,
        "fat": 9,
        "fiber": 2,
        "description": "Stir-fried rice with vegetables",
        "health_tips": "High carb content. Add more vegetables to increase fiber and nutrients."
    },
    "haleem": {
        "calories": 220,
        "protein": 14,
        "carbs": 25,
        "fat": 8,
        "fiber": 3,
        "description": "Slow-cooked meat and lentil stew",
        "health_tips": "Very nutritious, high in protein and fiber. Good during Ramadan for sustained energy."
    },
    "hilsha_fish": {
        "calories": 310,
        "protein": 22,
        "carbs": 0,
        "fat": 25,
        "fiber": 0,
        "description": "National fish of Bangladesh",
        "health_tips": "Very high in Omega-3 fatty acids. Good for heart and brain. High in healthy fats."
    },
    "jalebi": {
        "calories": 380,
        "protein": 3,
        "carbs": 60,
        "fat": 15,
        "fiber": 0,
        "description": "Deep-fried sweet spirals in sugar syrup",
        "health_tips": "⚠️ Very high in sugar and calories. Occasional treat only. Not suitable for diabetics."
    },
    "kabab": {
        "calories": 250,
        "protein": 20,
        "carbs": 8,
        "fat": 16,
        "fiber": 1,
        "description": "Grilled meat skewers",
        "health_tips": "High protein, good for muscle building. Choose grilled over fried versions."
    },
    "kacchi_biryani": {
        "calories": 320,
        "protein": 15,
        "carbs": 38,
        "fat": 14,
        "fiber": 1,
        "description": "Premium layered rice and meat dish",
        "health_tips": "Rich and heavy. Best for special occasions. High calorie - control portion size."
    },
    "kheer": {
        "calories": 180,
        "protein": 5,
        "carbs": 28,
        "fat": 6,
        "fiber": 0.5,
        "description": "Rice pudding dessert",
        "health_tips": "Good source of calcium from milk. Reduce sugar for healthier version."
    },
    "korma": {
        "calories": 200,
        "protein": 14,
        "carbs": 10,
        "fat": 12,
        "fiber": 1,
        "description": "Creamy meat curry",
        "health_tips": "Rich in protein. High fat from cream/nuts. Good occasional indulgence."
    },
    "misti_doi": {
        "calories": 150,
        "protein": 4,
        "carbs": 25,
        "fat": 4,
        "fiber": 0,
        "description": "Sweet yogurt dessert",
        "health_tips": "Contains probiotics for gut health. High sugar - enjoy in moderation."
    },
    "naan": {
        "calories": 260,
        "protein": 8,
        "carbs": 45,
        "fat": 5,
        "fiber": 2,
        "description": "Leavened flatbread",
        "health_tips": "Higher calories than chapati. Made with refined flour - choose whole wheat version."
    },
    "paratha": {
        "calories": 280,
        "protein": 6,
        "carbs": 35,
        "fat": 14,
        "fiber": 2,
        "description": "Layered flatbread with oil/ghee",
        "health_tips": "Higher fat content. Limit to occasional breakfast. Pair with protein for balance."
    },
    "polao": {
        "calories": 220,
        "protein": 5,
        "carbs": 38,
        "fat": 6,
        "fiber": 1,
        "description": "Fragrant spiced rice",
        "health_tips": "Lower fat than biryani. Good carb source. Add vegetables for more nutrition."
    },
    "pitha": {
        "calories": 200,
        "protein": 4,
        "carbs": 35,
        "fat": 6,
        "fiber": 1,
        "description": "Traditional rice cakes",
        "health_tips": "Traditional snack. Made with rice flour. Healthier than deep-fried snacks."
    },
    "rasmalai": {
        "calories": 280,
        "protein": 8,
        "carbs": 35,
        "fat": 12,
        "fiber": 0,
        "description": "Sweet cheese balls in cream",
        "health_tips": "⚠️ High sugar and fat. Special occasion dessert. Good calcium from milk."
    },
    "rezala": {
        "calories": 190,
        "protein": 16,
        "carbs": 8,
        "fat": 11,
        "fiber": 1,
        "description": "White meat curry from Kolkata",
        "health_tips": "High protein dish. Made with yogurt - contains probiotics."
    },
    "roti": {
        "calories": 100,
        "protein": 3,
        "carbs": 20,
        "fat": 1,
        "fiber": 2,
        "description": "Simple whole wheat bread",
        "health_tips": "Healthiest bread option. Low fat, good fiber. Best choice for weight watchers."
    },
    "samosa": {
        "calories": 260,
        "protein": 5,
        "carbs": 30,
        "fat": 14,
        "fiber": 2,
        "description": "Fried pastry with filling",
        "health_tips": "⚠️ Deep fried - high in trans fats. Choose baked version. Limit consumption."
    },
    "shingara": {
        "calories": 150,
        "protein": 3,
        "carbs": 18,
        "fat": 8,
        "fiber": 1,
        "description": "Smaller version of samosa",
        "health_tips": "Similar to samosa - fried snack. Occasional treat. Try air-fried version."
    },
    "shutki": {
        "calories": 350,
        "protein": 60,
        "carbs": 0,
        "fat": 10,
        "fiber": 0,
        "description": "Dried fish - protein dense",
        "health_tips": "Extremely high protein! Very high sodium - limit if hypertensive. Strong flavor."
    },
    "tehari": {
        "calories": 280,
        "protein": 12,
        "carbs": 40,
        "fat": 10,
        "fiber": 1,
        "description": "Beef rice dish",
        "health_tips": "High carbs and protein. Good energy food. Watch fat content from beef."
    },
    "vorta": {
        "calories": 80,
        "protein": 2,
        "carbs": 8,
        "fat": 5,
        "fiber": 2,
        "description": "Mashed vegetable/fish side dish",
        "health_tips": "Low calorie, nutritious side. Vegetable vortas are very healthy. Good fiber source."
    },
    # Default for unknown classes
    "default": {
        "calories": 200,
        "protein": 8,
        "carbs": 25,
        "fat": 8,
        "fiber": 2,
        "description": "Bangladeshi food item",
        "health_tips": "Enjoy in moderation as part of a balanced diet."
    }
}

# ============================================
# MODEL LOADING
# ============================================
def detect_model_architecture(state_dict):
    """Auto-detect model architecture from state_dict keys"""
    keys = list(state_dict.keys())
    first_key = keys[0] if keys else ""
    
    # Check for EfficientNet (has 'features.' prefix and 'classifier.')
    if any('features.' in k and 'block' in k for k in keys):
        # Count layers to determine B0 vs B3
        # EfficientNet-B3 has more parameters
        num_params = sum(p.numel() for p in state_dict.values())
        if num_params > 10_000_000:  # B3 has ~12M params, B0 has ~5M
            return "efficientnet_b3"
        else:
            return "efficientnet_b0"
    
    # Check for DenseNet (has 'features.denseblock')
    if any('denseblock' in k for k in keys):
        return "densenet121"
    
    # Check for ResNet (has 'layer1', 'layer2', etc.)
    if any('layer1' in k for k in keys):
        # ResNet50 has 'layer1.0.conv3' (bottleneck), ResNet18 doesn't
        if any('conv3' in k for k in keys):
            return "resnet50"
        else:
            return "resnet18"
    
    return "unknown"

@st.cache_resource
def load_model(model_path, class_names_path):
    """Load the trained model with auto-detection"""
    
    # Load class names
    with open(class_names_path, 'r') as f:
        class_dict = json.load(f)
    class_names = [class_dict[str(i)] for i in range(len(class_dict))]
    num_classes = len(class_names)
    
    # Load state dict first to detect architecture
    state_dict = torch.load(model_path, map_location=torch.device('cpu'))
    
    # Auto-detect model architecture
    detected_arch = detect_model_architecture(state_dict)
    st.info(f"🔍 Detected model: **{detected_arch.upper()}**")
    
    # Create model architecture based on detection
    if detected_arch == "resnet18":
        model = models.resnet18(weights=None)
        model.fc = nn.Linear(model.fc.in_features, num_classes)
    elif detected_arch == "resnet50":
        model = models.resnet50(weights=None)
        model.fc = nn.Linear(model.fc.in_features, num_classes)
    elif detected_arch == "efficientnet_b0":
        model = models.efficientnet_b0(weights=None)
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    elif detected_arch == "efficientnet_b3":
        model = models.efficientnet_b3(weights=None)
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    elif detected_arch == "densenet121":
        model = models.densenet121(weights=None)
        model.classifier = nn.Linear(model.classifier.in_features, num_classes)
    else:
        raise ValueError(f"Could not detect model architecture. Keys: {list(state_dict.keys())[:5]}")
    
    # Load weights
    model.load_state_dict(state_dict)
    model.eval()
    
    return model, class_names, detected_arch

# ============================================
# PREDICTION FUNCTION
# ============================================
def predict_food(image, model, class_names):
    """Predict food class from image"""
    
    # Transform
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    # Preprocess
    img_tensor = transform(image).unsqueeze(0)
    
    # Predict
    with torch.no_grad():
        outputs = model(img_tensor)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        confidence, predicted = torch.max(probabilities, 1)
    
    predicted_class = class_names[predicted.item()]
    confidence_score = confidence.item() * 100
    
    # Get top 3 predictions
    top3_prob, top3_idx = torch.topk(probabilities, 3)
    top3 = [(class_names[idx.item()], prob.item() * 100) 
            for idx, prob in zip(top3_idx[0], top3_prob[0])]
    
    return predicted_class, confidence_score, top3

def get_nutrition(food_name):
    """Get nutrition data for food"""
    # Normalize food name
    food_key = food_name.lower().replace(" ", "_").replace("-", "_")
    
    # Try to find matching nutrition data
    for key in NUTRITION_DATA:
        if key in food_key or food_key in key:
            return NUTRITION_DATA[key]
    
    return NUTRITION_DATA["default"]

# ============================================
# STREAMLIT UI
# ============================================
def main():
    st.title("🍛 Bangladeshi Food Classifier")
    st.markdown("### AI-Powered Food Recognition & Nutrition Advisor")
    st.markdown("---")
    
    # Sidebar for model settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Model file upload
        st.subheader("📁 Upload Model Files")
        model_file = st.file_uploader("Upload trained model (.pth)", type=['pth'])
        class_file = st.file_uploader("Upload class_names.json", type=['json'])
        
        if model_file and class_file:
            # Save uploaded files
            os.makedirs("uploaded_model", exist_ok=True)
            
            with open("uploaded_model/model.pth", "wb") as f:
                f.write(model_file.getbuffer())
            with open("uploaded_model/class_names.json", "wb") as f:
                f.write(class_file.getbuffer())
            
            st.success("✅ Model files uploaded!")
        
        st.markdown("---")
        st.subheader("ℹ️ About")
        st.markdown("""
        This app uses deep learning to:
        - 🔍 Identify Bangladeshi foods
        - 📊 Show nutrition information
        - 💡 Provide health tips
        
        **Thesis Project** - Food Classification
        """)
    
    # Check if model is available
    model_path = "uploaded_model/model.pth"
    class_path = "uploaded_model/class_names.json"
    
    if not (os.path.exists(model_path) and os.path.exists(class_path)):
        st.warning("⚠️ Please upload your trained model files in the sidebar first!")
        st.info("""
        **How to use:**
        1. Upload your `best_model_*.pth` file
        2. Upload your `class_names.json` file
        3. Then upload a food image to classify!
        """)
        
        # Demo mode with sample nutrition info
        st.markdown("---")
        st.subheader("📚 Sample Nutrition Database")
        
        cols = st.columns(3)
        sample_foods = ["biryani", "dal", "fish_curry"]
        for i, food in enumerate(sample_foods):
            with cols[i]:
                nutrition = NUTRITION_DATA[food]
                st.markdown(f"**{food.replace('_', ' ').title()}**")
                st.markdown(f"🔥 {nutrition['calories']} kcal")
                st.markdown(f"🥩 Protein: {nutrition['protein']}g")
                st.markdown(f"🍚 Carbs: {nutrition['carbs']}g")
        
        return
    
    # Load model
    try:
        model, class_names, detected_arch = load_model(model_path, class_path)
        st.success(f"✅ Model loaded! ({len(class_names)} food classes)")
    except Exception as e:
        st.error(f"❌ Error loading model: {e}")
        return
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📤 Upload Food Image")
        uploaded_image = st.file_uploader(
            "Choose an image...", 
            type=['jpg', 'jpeg', 'png', 'webp']
        )
        
        if uploaded_image:
            image = Image.open(uploaded_image).convert('RGB')
            st.image(image, caption="Uploaded Image", use_container_width=True)
            
            # Predict button
            if st.button("🔍 Analyze Food", type="primary"):
                with st.spinner("Analyzing..."):
                    predicted_class, confidence, top3 = predict_food(image, model, class_names)
                
                # Store results in session state
                st.session_state['prediction'] = {
                    'class': predicted_class,
                    'confidence': confidence,
                    'top3': top3
                }
    
    with col2:
        st.subheader("📊 Results")
        
        if 'prediction' in st.session_state:
            pred = st.session_state['prediction']
            
            # Main prediction
            st.markdown(f"### 🍽️ **{pred['class'].replace('_', ' ').title()}**")
            st.progress(pred['confidence'] / 100)
            st.markdown(f"**Confidence: {pred['confidence']:.1f}%**")
            
            # Top 3 predictions
            st.markdown("---")
            st.markdown("**Top 3 Predictions:**")
            for food, conf in pred['top3']:
                st.markdown(f"- {food.replace('_', ' ').title()}: {conf:.1f}%")
            
            # Nutrition info
            st.markdown("---")
            nutrition = get_nutrition(pred['class'])
            
            st.markdown("### 📋 Nutrition Facts (per 100g)")
            
            # Nutrition metrics
            met_cols = st.columns(4)
            met_cols[0].metric("🔥 Calories", f"{nutrition['calories']} kcal")
            met_cols[1].metric("🥩 Protein", f"{nutrition['protein']}g")
            met_cols[2].metric("🍚 Carbs", f"{nutrition['carbs']}g")
            met_cols[3].metric("🧈 Fat", f"{nutrition['fat']}g")
            
            # Description and tips
            st.markdown("---")
            st.markdown(f"**📝 Description:** {nutrition['description']}")
            st.info(f"💡 **Health Tips:** {nutrition['health_tips']}")
        else:
            st.info("👆 Upload an image and click 'Analyze Food' to see results")

if __name__ == "__main__":
    main()
