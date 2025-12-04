"""
🍛 Bangladeshi Food Classifier & Nutrition Advisor
A modern Streamlit app for food image classification with comprehensive nutrition information

To run: streamlit run food_classifier_app.py
"""

import streamlit as st
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import json
import os
import time

# Page config
st.set_page_config(
    page_title="🍛 Bangladeshi Food Classifier",
    page_icon="🍛",
    layout="wide",
    initial_sidebar_state="auto"
)

# Custom CSS for modern design with mobile responsiveness
st.markdown("""
<style>
    /* Mobile-First Responsive Design */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        font-size: clamp(1.5rem, 4vw, 2.5rem);
        margin-bottom: 0.5rem;
    }
    
    .main-header p {
        font-size: clamp(0.9rem, 2vw, 1.2rem);
    }
    
    .food-card {
        background: white;
        padding: 1rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 5px solid #667eea;
    }
    
    .prediction-badge {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 0.75rem 1.5rem;
        border-radius: 50px;
        color: white;
        font-size: clamp(1.1rem, 3vw, 1.5rem);
        font-weight: bold;
        display: inline-block;
        margin: 0.75rem 0;
        word-break: break-word;
    }
    
    .info-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.75rem 0;
        font-size: clamp(0.85rem, 2vw, 1rem);
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 25px;
        padding: 0.75rem 1.5rem;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        transition: all 0.3s;
        width: 100%;
        font-size: clamp(0.9rem, 2.5vw, 1.1rem);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0,0,0,0.3);
    }
    
    /* Mobile Optimization */
    @media (max-width: 768px) {
        .main-header {
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
        
        .food-card, .info-section {
            padding: 0.75rem;
            margin: 0.5rem 0;
            border-radius: 10px;
        }
        
        .prediction-badge {
            padding: 0.5rem 1rem;
            font-size: 1rem;
        }
        
        /* Stack columns on mobile */
        .stColumn {
            width: 100% !important;
            flex: 1 1 100% !important;
            max-width: 100% !important;
        }
        
        /* Adjust sidebar for mobile */
        section[data-testid="stSidebar"] {
            width: 100% !important;
            min-width: auto !important;
        }
        
        /* Make images responsive */
        img {
            max-width: 100%;
            height: auto;
        }
        
        /* Adjust text sizes */
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.3rem !important; }
        h3 { font-size: 1.1rem !important; }
        p { font-size: 0.9rem !important; }
    }
    
    @media (max-width: 480px) {
        .main-header {
            padding: 0.75rem;
        }
        
        .main-header h1 {
            font-size: 1.25rem;
        }
        
        .main-header p {
            font-size: 0.85rem;
        }
        
        .stButton>button {
            padding: 0.6rem 1rem;
            font-size: 0.9rem;
        }
    }
    
    /* Touch-friendly elements */
    @media (hover: none) and (pointer: coarse) {
        .stButton>button, a, input, select {
            min-height: 44px;
            min-width: 44px;
        }
    }
    
    /* PWA Install Banner */
    .install-banner {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 50px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 1000;
        display: none;
        font-size: 0.9rem;
        text-align: center;
    }
    
    .install-banner.show {
        display: block;
    }
</style>

<!-- PWA Meta Tags -->
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Food Classifier">
<meta name="theme-color" content="#667eea">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">

<!-- PWA Service Worker Registration -->
<script>
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
            navigator.serviceWorker.register('/service-worker.js')
                .then(function(registration) {
                    console.log('ServiceWorker registered:', registration.scope);
                })
                .catch(function(error) {
                    console.log('ServiceWorker registration failed:', error);
                });
        });
    }
    
    // PWA Install Prompt
    let deferredPrompt;
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        
        // Show install banner
        const banner = document.querySelector('.install-banner');
        if (banner) {
            banner.classList.add('show');
        }
    });
    
    // Check if running as PWA
    if (window.matchMedia('(display-mode: standalone)').matches) {
        console.log('Running as PWA');
    }
</script>
""", unsafe_allow_html=True)

# ============================================
# COMPREHENSIVE NUTRITION DATABASE
# ============================================
NUTRITION_DATA = {
    "biryani": {
        "calories": 290, "protein": 12, "carbs": 35, "fat": 12, "fiber": 1.5,
        "description": "Aromatic layered rice dish with marinated meat, fragrant spices, and fried onions",
        "origin": "Dhaka, Chittagong, Sylhet (influenced by Mughal cuisine)",
        "preparation": "Rice and meat cooked separately, then layered with saffron, ghee, and fried onions. Sealed and slow-cooked (dum) to perfection.",
        "best_time": "Lunch or special occasions",
        "health_tips": "High in carbs and protein - good post-workout meal. Watch portion size due to oil content. Opt for brown rice version for more fiber.",
        "vitamins": "B vitamins (B6, B12), Iron, Zinc",
        "serving_size": "1 plate (250g) = 725 calories",
        "popular_variants": "Kacchi Biryani, Morog Polao, Tehari"
    },
    "bhuna_khichuri": {
        "calories": 180, "protein": 6, "carbs": 28, "fat": 5, "fiber": 3,
        "description": "Comfort food made with rice and lentils, cooked together with aromatic spices",
        "origin": "Rural Bengal, popular across Bangladesh",
        "preparation": "Rice and lentils roasted in ghee with onions and spices, then simmered with water until creamy. Often served with fried eggplant.",
        "best_time": "Rainy days, winter evenings",
        "health_tips": "Complete protein source when rice and lentils combine. Easy to digest. Great for weight management.",
        "vitamins": "Folate, Iron, Magnesium, B vitamins",
        "serving_size": "1 bowl (200g) = 360 calories",
        "popular_variants": "Plain Khichuri, Bhuna Khichuri, Moong Dal Khichuri"
    },
    "chapati": {
        "calories": 120, "protein": 4, "carbs": 25, "fat": 1, "fiber": 2,
        "description": "Whole wheat flatbread - staple in Bangladeshi households",
        "origin": "Common across Bangladesh, influenced by North Indian cuisine",
        "preparation": "Whole wheat dough rolled thin and cooked on a hot griddle (tawa) without oil. Puffed over open flame for softness.",
        "best_time": "Any meal - breakfast, lunch, dinner",
        "health_tips": "Low fat, high fiber. Better than white rice for blood sugar control. Good for diabetics and weight watchers.",
        "vitamins": "B vitamins, Iron, Magnesium",
        "serving_size": "1 piece (50g) = 60 calories",
        "popular_variants": "Plain Chapati, Atta Roti, Missi Roti"
    },
    "chicken_curry": {
        "calories": 180, "protein": 18, "carbs": 8, "fat": 10, "fiber": 1,
        "description": "Traditional chicken cooked in rich, spiced gravy",
        "origin": "Popular nationwide - Dhaka, Chittagong, Sylhet",
        "preparation": "Chicken marinated in spices, cooked with onion-tomato-ginger-garlic paste, finished with garam masala and fresh coriander.",
        "best_time": "Lunch or dinner",
        "health_tips": "Excellent protein source. Choose skinless chicken for lower fat. Rich in selenium and B vitamins for metabolism.",
        "vitamins": "B6, B12, Niacin, Selenium, Phosphorus",
        "serving_size": "1 serving (150g) = 270 calories",
        "popular_variants": "Rezala, Korma, Roast, Jhol (curry)"
    },
    "dal": {
        "calories": 120, "protein": 8, "carbs": 20, "fat": 2, "fiber": 4,
        "description": "Lentil soup - the heart of Bengali meals, cooked with turmeric and spices",
        "origin": "Universal across Bangladesh - daily staple",
        "preparation": "Lentils boiled with turmeric, tempered with garlic, onion, dried chilies in mustard oil. Finished with fresh coriander.",
        "best_time": "Every meal - breakfast, lunch, dinner",
        "health_tips": "Plant-based protein powerhouse. High fiber aids digestion. Low fat and heart-healthy. Great for vegans.",
        "vitamins": "Folate, Iron, Magnesium, Potassium, Zinc",
        "serving_size": "1 bowl (200ml) = 240 calories",
        "popular_variants": "Masoor Dal, Moong Dal, Chana Dal, Mixed Dal"
    },
    "egg_curry": {
        "calories": 150, "protein": 10, "carbs": 5, "fat": 11, "fiber": 1,
        "description": "Hard-boiled eggs in spiced tomato-onion gravy",
        "origin": "Popular across Bangladesh, affordable protein source",
        "preparation": "Boiled eggs fried lightly, then simmered in curry made with onion, tomato, ginger-garlic paste, and aromatic spices.",
        "best_time": "Any meal - common breakfast with paratha",
        "health_tips": "Complete protein with all essential amino acids. Rich in vitamin B12, choline for brain health. Budget-friendly nutrition.",
        "vitamins": "B12, D, A, Choline, Selenium",
        "serving_size": "2 eggs with gravy (150g) = 225 calories",
        "popular_variants": "Dim Bhuna, Dimer Dalna, Egg Masala"
    },
    "fish_curry": {
        "calories": 140, "protein": 16, "carbs": 6, "fat": 6, "fiber": 0.5,
        "description": "Fresh fish cooked in traditional Bengali spices",
        "origin": "Nationwide - Bangladesh is land of rivers",
        "preparation": "Fish marinated with turmeric, lightly fried, then cooked in gravy with mustard, nigella seeds, and green chilies.",
        "best_time": "Lunch or dinner",
        "health_tips": "Omega-3 rich for heart and brain health. High-quality protein. Choose small fish for calcium from bones.",
        "vitamins": "Omega-3, D, B12, Selenium, Iodine",
        "serving_size": "1 serving (150g) = 210 calories",
        "popular_variants": "Rui Curry, Katla Jhol, Hilsha Curry, Pabda Curry"
    },
    "fried_rice": {
        "calories": 250, "protein": 8, "carbs": 35, "fat": 9, "fiber": 2,
        "description": "Stir-fried rice with vegetables, eggs, and soy sauce",
        "origin": "Chinese-influenced, popular in Dhaka and urban areas",
        "preparation": "Day-old rice stir-fried on high heat with vegetables, eggs, soy sauce, and optional chicken or shrimp.",
        "best_time": "Lunch or dinner",
        "health_tips": "Moderate calories. Add more vegetables for fiber and nutrients. Use brown rice for healthier version.",
        "vitamins": "B vitamins, Vitamin A (from carrots), Iron",
        "serving_size": "1 plate (250g) = 625 calories",
        "popular_variants": "Chicken Fried Rice, Vegetable Fried Rice, Shrimp Fried Rice"
    },
    "haleem": {
        "calories": 220, "protein": 14, "carbs": 25, "fat": 8, "fiber": 3,
        "description": "Slow-cooked stew of meat, lentils, wheat, and spices - Ramadan special",
        "origin": "Dhaka, especially Old Dhaka during Ramadan",
        "preparation": "Meat, wheat, barley, and lentils slow-cooked for 7-8 hours until thick paste-like consistency. Garnished with fried onions, mint, lemon.",
        "best_time": "Iftar during Ramadan",
        "health_tips": "Very nutritious and filling. High protein and fiber for sustained energy. Perfect for breaking fast.",
        "vitamins": "Iron, B vitamins, Zinc, Magnesium",
        "serving_size": "1 bowl (200g) = 440 calories",
        "popular_variants": "Beef Haleem, Mutton Haleem, Chicken Haleem"
    },
    "hilsha_fish": {
        "calories": 310, "protein": 22, "carbs": 0, "fat": 25, "fiber": 0,
        "description": "National fish of Bangladesh - prized for rich, oily flesh",
        "origin": "Padma River, Meghna River, coastal regions",
        "preparation": "Steamed with mustard paste, cooked in curry with minimal spices to preserve flavor, or fried with turmeric.",
        "best_time": "Monsoon season (June-September) when it's most flavorful",
        "health_tips": "Extremely high in Omega-3 fatty acids. Excellent for heart and brain. High healthy fat content. Good for pregnant women.",
        "vitamins": "Omega-3, D, B12, Selenium, Calcium",
        "serving_size": "1 piece (100g) = 310 calories",
        "popular_variants": "Ilish Bhapa, Shorshe Ilish, Ilish Bhaja"
    },
    "jalebi": {
        "calories": 380, "protein": 3, "carbs": 60, "fat": 15, "fiber": 0,
        "description": "Deep-fried spiral-shaped sweet soaked in sugar syrup",
        "origin": "Old Dhaka, popular across Bangladesh",
        "preparation": "Fermented batter piped in spirals into hot oil, fried until crispy, immediately soaked in warm sugar syrup flavored with saffron.",
        "best_time": "Special occasions, festivals, weddings",
        "health_tips": "⚠️ Very high in sugar and calories. Occasional treat only. Not suitable for diabetics. Consume in small portions.",
        "vitamins": "Minimal nutritional value - primarily sugar and fat",
        "serving_size": "2 pieces (100g) = 380 calories",
        "popular_variants": "Crispy Jalebi, Paneer Jalebi, Imarti"
    },
    "kabab": {
        "calories": 250, "protein": 20, "carbs": 8, "fat": 16, "fiber": 1,
        "description": "Spiced minced meat skewers, grilled or fried",
        "origin": "Dhaka, Chittagong - Mughal influence",
        "preparation": "Minced meat mixed with spices, onions, eggs, shaped into patties or skewers, then grilled over charcoal or shallow fried.",
        "best_time": "Snacks, iftar, dinner appetizer",
        "health_tips": "High protein for muscle building. Choose grilled over fried. Good source of iron and B vitamins.",
        "vitamins": "B12, B6, Iron, Zinc, Selenium",
        "serving_size": "2 pieces (100g) = 250 calories",
        "popular_variants": "Shami Kabab, Seekh Kabab, Chapli Kabab, Shish Kabab"
    },
    "kacchi_biryani": {
        "calories": 320, "protein": 15, "carbs": 38, "fat": 14, "fiber": 1,
        "description": "Premium biryani with raw marinated meat and rice cooked together",
        "origin": "Old Dhaka - specialty of Dhaka city",
        "preparation": "Raw marinated meat layered with partially cooked rice, sealed with dough, slow-cooked on dum (steam) for 45-60 minutes.",
        "best_time": "Special occasions, weddings, celebrations",
        "health_tips": "Rich and calorie-dense. Best for special occasions. Contains high-quality protein and complex carbs.",
        "vitamins": "B vitamins, Iron, Zinc, Selenium",
        "serving_size": "1 plate (250g) = 800 calories",
        "popular_variants": "Beef Kacchi, Mutton Kacchi, Morog Polao"
    },
    "kheer": {
        "calories": 180, "protein": 5, "carbs": 28, "fat": 6, "fiber": 0.5,
        "description": "Rice pudding dessert with milk, sugar, cardamom, and nuts",
        "origin": "Popular across Bangladesh - festival special",
        "preparation": "Rice slow-cooked in milk until creamy, sweetened with sugar, flavored with cardamom, garnished with pistachios and almonds.",
        "best_time": "Dessert after meals, Eid celebrations",
        "health_tips": "Good calcium source from milk. Reduce sugar for healthier version. Rich in protein from milk.",
        "vitamins": "Calcium, Vitamin D, B12, Phosphorus",
        "serving_size": "1 bowl (150g) = 270 calories",
        "popular_variants": "Firni, Payesh, Semai"
    },
    "korma": {
        "calories": 200, "protein": 14, "carbs": 10, "fat": 12, "fiber": 1,
        "description": "Creamy meat curry with yogurt, cream, and ground nuts",
        "origin": "Dhaka, Old Dhaka - Mughal cuisine heritage",
        "preparation": "Meat slow-cooked in yogurt-cream gravy with ground cashews, almonds, mild spices. Rich and aromatic.",
        "best_time": "Special occasions, dinner parties",
        "health_tips": "Rich in protein and healthy fats from nuts. High calorie - enjoy in moderation. Good occasional indulgence.",
        "vitamins": "B12, Calcium, Magnesium, Healthy fats",
        "serving_size": "1 serving (150g) = 300 calories",
        "popular_variants": "Chicken Korma, Mutton Korma, Vegetable Korma"
    },
    "misti_doi": {
        "calories": 150, "protein": 4, "carbs": 25, "fat": 4, "fiber": 0,
        "description": "Sweet fermented yogurt - Bengali signature dessert",
        "origin": "Bogra (famous for its Bogra Doi), popular nationwide",
        "preparation": "Milk reduced and caramelized with sugar, fermented in clay pots overnight, giving distinctive sweet-tangy flavor.",
        "best_time": "Dessert, afternoon snack",
        "health_tips": "Contains probiotics for gut health. Good calcium source. High sugar - consume in moderation.",
        "vitamins": "Calcium, B12, Probiotics, Phosphorus",
        "serving_size": "1 cup (150g) = 225 calories",
        "popular_variants": "Bogra Doi, Chomchom, Rosogolla"
    },
    "naan": {
        "calories": 260, "protein": 8, "carbs": 45, "fat": 5, "fiber": 2,
        "description": "Leavened flatbread baked in tandoor oven",
        "origin": "Restaurant culture - Dhaka, Chittagong",
        "preparation": "Refined flour dough with yeast, stretched and slapped onto walls of hot tandoor oven until puffed and charred spots appear.",
        "best_time": "Lunch or dinner with curry",
        "health_tips": "Higher calories than chapati due to refined flour. Choose whole wheat naan for better nutrition.",
        "vitamins": "B vitamins, Iron, Folate",
        "serving_size": "1 piece (100g) = 260 calories",
        "popular_variants": "Butter Naan, Garlic Naan, Keema Naan"
    },
    "paratha": {
        "calories": 280, "protein": 6, "carbs": 35, "fat": 14, "fiber": 2,
        "description": "Layered flatbread with oil or ghee",
        "origin": "Common across Bangladesh - breakfast staple",
        "preparation": "Wheat dough rolled thin, brushed with oil/ghee, folded multiple times for layers, then shallow fried until crispy and flaky.",
        "best_time": "Breakfast",
        "health_tips": "Higher fat content than chapati. Limit to occasional breakfast. Pair with protein for balanced meal.",
        "vitamins": "B vitamins, Iron, Magnesium",
        "serving_size": "1 piece (75g) = 210 calories",
        "popular_variants": "Plain Paratha, Aloo Paratha, Egg Paratha, Mughlai Paratha"
    },
    "polao": {
        "calories": 220, "protein": 5, "carbs": 38, "fat": 6, "fiber": 1,
        "description": "Fragrant spiced rice - lighter version of biryani",
        "origin": "Popular across Bangladesh",
        "preparation": "Basmati rice cooked with ghee, whole spices (cinnamon, cardamom, bay leaf), and meat/vegetable stock for aromatic flavor.",
        "best_time": "Lunch, special occasions",
        "health_tips": "Lower fat than biryani. Good carb source. Add vegetables for more nutrition. Use less ghee for healthier version.",
        "vitamins": "B vitamins, Iron",
        "serving_size": "1 plate (200g) = 440 calories",
        "popular_variants": "Morog Polao, Vegetable Polao, Tehari"
    },
    "pitha": {
        "calories": 200, "protein": 4, "carbs": 35, "fat": 6, "fiber": 1,
        "description": "Traditional rice cakes - winter specialty",
        "origin": "Rural Bengal, winter festivals (Poush Parbon)",
        "preparation": "Rice flour mixed with jaggery/coconut, shaped and steamed, fried, or cooked on griddle. Many regional varieties.",
        "best_time": "Winter season, breakfast, snacks",
        "health_tips": "Traditional snack, moderate calories. Made with rice flour - gluten-free. Healthier than deep-fried snacks when steamed.",
        "vitamins": "B vitamins, Iron (from jaggery)",
        "serving_size": "2 pieces (100g) = 200 calories",
        "popular_variants": "Chitoi Pitha, Bhapa Pitha, Patishapta, Nakshi Pitha"
    },
    "rasmalai": {
        "calories": 280, "protein": 8, "carbs": 35, "fat": 12, "fiber": 0,
        "description": "Soft cheese patties in sweetened, thickened milk with cardamom",
        "origin": "Comilla (birthplace of Rasmalai), popular nationwide",
        "preparation": "Fresh cheese (paneer) shaped into discs, cooked in light syrup, then soaked in reduced milk flavored with saffron and cardamom.",
        "best_time": "Dessert, special occasions, Eid",
        "health_tips": "⚠️ High sugar and fat. Special occasion dessert. Good calcium from milk and cheese. Enjoy small portions.",
        "vitamins": "Calcium, Protein, Vitamin D, B12",
        "serving_size": "2 pieces (100g) = 280 calories",
        "popular_variants": "Rasgulla, Chamcham, Sandesh"
    },
    "rezala": {
        "calories": 190, "protein": 16, "carbs": 8, "fat": 11, "fiber": 1,
        "description": "White meat curry - Kolkata-style but popular in Bangladesh",
        "origin": "Dhaka (influenced by Kolkata), Old Dhaka restaurants",
        "preparation": "Meat marinated in yogurt and spices, cooked in white gravy made with cashew paste, poppy seeds, yogurt, and minimal turmeric.",
        "best_time": "Dinner, special occasions",
        "health_tips": "High protein. Yogurt-based makes it easier to digest. Contains probiotics from yogurt. Rich in B vitamins.",
        "vitamins": "B12, B6, Calcium, Probiotics, Selenium",
        "serving_size": "1 serving (150g) = 285 calories",
        "popular_variants": "Chicken Rezala, Mutton Rezala"
    },
    "roti": {
        "calories": 100, "protein": 3, "carbs": 20, "fat": 1, "fiber": 2,
        "description": "Simple whole wheat bread - healthiest bread option",
        "origin": "Common across Bangladesh",
        "preparation": "Whole wheat dough rolled thin, cooked on griddle without oil or with minimal oil. Simple and nutritious.",
        "best_time": "Any meal",
        "health_tips": "Healthiest bread choice. Low fat, good fiber. Best for weight management and diabetics. Provides sustained energy.",
        "vitamins": "B vitamins, Iron, Magnesium, Fiber",
        "serving_size": "1 piece (40g) = 40 calories",
        "popular_variants": "Tandoori Roti, Rumali Roti, Chapati"
    },
    "samosa": {
        "calories": 260, "protein": 5, "carbs": 30, "fat": 14, "fiber": 2,
        "description": "Triangular fried pastry with spiced potato/meat filling",
        "origin": "Popular street food across Bangladesh",
        "preparation": "Thin pastry dough filled with spiced mashed potatoes or minced meat, shaped into triangles, deep-fried until golden and crispy.",
        "best_time": "Evening snack, iftar",
        "health_tips": "⚠️ Deep fried - high in trans fats. Occasional treat. Choose baked version or air-fried. Limit consumption for heart health.",
        "vitamins": "Vitamin C (from potatoes), B vitamins, Iron",
        "serving_size": "2 pieces (100g) = 260 calories",
        "popular_variants": "Vegetable Samosa, Meat Samosa, Chicken Samosa"
    },
    "shingara": {
        "calories": 150, "protein": 3, "carbs": 18, "fat": 8, "fiber": 1,
        "description": "Smaller, crispier version of samosa - Bengali street food icon",
        "origin": "Street food culture - Dhaka, Chittagong, everywhere",
        "preparation": "Similar to samosa but smaller, with thinner crust and spicier filling. Served with tamarind chutney or green chili.",
        "best_time": "Evening snack with tea",
        "health_tips": "Similar to samosa - fried snack. Occasional indulgence. Try air-fried or baked versions at home.",
        "vitamins": "Vitamin C, B vitamins, Potassium",
        "serving_size": "3 pieces (100g) = 150 calories",
        "popular_variants": "Aloo Shingara, Beef Shingara, Mixed Shingara"
    },
    "shutki": {
        "calories": 350, "protein": 60, "carbs": 0, "fat": 10, "fiber": 0,
        "description": "Dried fish - protein-dense traditional preservation method",
        "origin": "Coastal regions - Chittagong, Cox's Bazar",
        "preparation": "Small fish dried in sun, then fried with onions, garlic, and chilies. Strong, pungent flavor loved by many.",
        "best_time": "Lunch as side dish with rice",
        "health_tips": "Extremely high protein! Very high sodium - limit if hypertensive. Rich in omega-3. Strong acquired taste.",
        "vitamins": "Omega-3, Calcium, Phosphorus, B12, D",
        "serving_size": "Small portion (50g) = 175 calories",
        "popular_variants": "Loitta Shutki, Chingri Shutki, Rupchanda Shutki"
    },
    "tehari": {
        "calories": 280, "protein": 12, "carbs": 40, "fat": 10, "fiber": 1,
        "description": "Yellow rice with beef - Old Dhaka specialty",
        "origin": "Old Dhaka (originated as budget-friendly biryani)",
        "preparation": "Beef cooked with mustard oil and spices, rice cooked separately with turmeric for yellow color, then mixed together.",
        "best_time": "Lunch",
        "health_tips": "High carbs and protein - good energy food. Contains turmeric (anti-inflammatory). Watch fat content from beef.",
        "vitamins": "B vitamins, Iron, Zinc, Curcumin (from turmeric)",
        "serving_size": "1 plate (250g) = 700 calories",
        "popular_variants": "Beef Tehari, Mutton Tehari"
    },
    "vorta": {
        "calories": 80, "protein": 2, "carbs": 8, "fat": 5, "fiber": 2,
        "description": "Mashed vegetable or fish side dish with mustard oil and chilies",
        "origin": "Rural Bengal, traditional home cooking",
        "preparation": "Vegetables (eggplant, potato) or small fish boiled/roasted, then mashed with raw mustard oil, onions, green chilies, and salt.",
        "best_time": "Lunch or dinner as side dish",
        "health_tips": "Very low calorie and nutritious. Vegetable vortas are excellent fiber sources. Mustard oil has omega-3.",
        "vitamins": "Varies by ingredient - usually Vitamin C, Potassium, Fiber",
        "serving_size": "1 serving (100g) = 80 calories",
        "popular_variants": "Begun Vorta (eggplant), Aloo Vorta (potato), Shutki Vorta, Ilish Vorta"
    }
}

# ============================================
# MODEL FUNCTIONS
# ============================================
def detect_model_architecture(state_dict):
    """Auto-detect model architecture from state_dict keys"""
    keys = list(state_dict.keys())
    
    if any('features.' in k and 'block' in k for k in keys):
        num_params = sum(p.numel() for p in state_dict.values())
        return "EfficientNet-B3" if num_params > 10_000_000 else "EfficientNet-B0"
    
    if any('denseblock' in k for k in keys):
        return "DenseNet-121"
    
    if any('layer1' in k for k in keys):
        return "ResNet-50" if any('conv3' in k for k in keys) else "ResNet-18"
    
    return "Unknown"

@st.cache_resource
def load_model(model_path, class_names_path):
    """Load trained model with auto-detection"""
    with open(class_names_path, 'r') as f:
        class_dict = json.load(f)
    class_names = [class_dict[str(i)] for i in range(len(class_dict))]
    num_classes = len(class_names)
    
    state_dict = torch.load(model_path, map_location=torch.device('cpu'))
    detected_arch = detect_model_architecture(state_dict)
    
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
    model.eval()
    
    return model, class_names, detected_arch

def predict_food(image, model, class_names, use_tta=True, num_augmentations=5):
    """Predict food class from image with Test-Time Augmentation (TTA)
    
    Args:
        image: PIL Image
        model: PyTorch model
        class_names: List of class names
        use_tta: Whether to use test-time augmentation (default: True)
        num_augmentations: Number of augmentations for TTA (default: 5)
    """
    # Base transform
    base_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    if not use_tta:
        # Standard prediction without TTA
        img_tensor = base_transform(image).unsqueeze(0)
        with torch.no_grad():
            outputs = model(img_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
    else:
        # Test-Time Augmentation for better accuracy
        all_predictions = []
        
        # Original prediction
        img_tensor = base_transform(image).unsqueeze(0)
        with torch.no_grad():
            outputs = model(img_tensor)
            all_predictions.append(torch.nn.functional.softmax(outputs, dim=1))
        
        # Augmented predictions
        tta_transforms = [
            # Horizontal flip
            transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.RandomHorizontalFlip(p=1.0),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ]),
            # Slight rotation
            transforms.Compose([
                transforms.Resize((240, 240)),
                transforms.RandomRotation(10),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ]),
            # Color jitter
            transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ColorJitter(brightness=0.2, contrast=0.2),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ]),
            # Random crop
            transforms.Compose([
                transforms.Resize((256, 256)),
                transforms.RandomResizedCrop(224, scale=(0.9, 1.0)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])
        ]
        
        # Apply augmentations and get predictions
        for i, tta_transform in enumerate(tta_transforms[:num_augmentations-1]):
            try:
                img_aug = tta_transform(image).unsqueeze(0)
                with torch.no_grad():
                    outputs = model(img_aug)
                    all_predictions.append(torch.nn.functional.softmax(outputs, dim=1))
            except Exception:
                continue  # Skip if augmentation fails
        
        # Average predictions from all augmentations
        probabilities = torch.stack(all_predictions).mean(dim=0)
    
    confidence, predicted = torch.max(probabilities, 1)
    predicted_class = class_names[predicted.item()]
    confidence_score = confidence.item() * 100
    
    # Get top 3 predictions
    top3_prob, top3_idx = torch.topk(probabilities, min(3, len(class_names)))
    top3 = [(class_names[idx.item()], prob.item() * 100) 
            for idx, prob in zip(top3_idx[0], top3_prob[0])]
    
    return predicted_class, confidence_score, top3

def get_nutrition(food_name):
    """Get nutrition data for food"""
    food_key = food_name.lower().replace(" ", "_").replace("-", "_")
    
    for key in NUTRITION_DATA:
        if key in food_key or food_key in key:
            return NUTRITION_DATA[key]
    
    return {
        "calories": 200, "protein": 8, "carbs": 25, "fat": 8, "fiber": 2,
        "description": "Bangladeshi food item",
        "origin": "Bangladesh",
        "preparation": "Traditional Bengali cooking method",
        "best_time": "Lunch or dinner",
        "health_tips": "Enjoy in moderation as part of a balanced diet.",
        "vitamins": "Various nutrients",
        "serving_size": "Standard serving",
        "popular_variants": "Multiple regional variations"
    }

# ============================================
# MAIN APP
# ============================================
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>Bangladeshi Food Classifier</h1>
        <p style="font-size: 1.2rem; margin-top: 1rem;">AI-Powered Food Recognition & Comprehensive Nutrition Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📊 About This App")
        st.markdown("""
        This intelligent system uses **deep learning** to:
        - 🔍 Identify 33 Bangladeshi foods
        - 📊 Provide detailed nutrition facts
        - 🗺️ Show regional origins
        - 👨‍🍳 Explain preparation methods
        - 💡 Offer health recommendations
        """)
        
        st.markdown("---")
        st.markdown("### 🔬 Advanced Settings")
        use_tta = st.checkbox(
            "Use Test-Time Augmentation",
            value=True,
            help="TTA improves accuracy by analyzing multiple versions of your image (2-3% better accuracy, slightly slower)"
        )
        
        if use_tta:
            num_augmentations = st.slider(
                "Augmentation strength",
                min_value=2,
                max_value=5,
                value=5,
                help="More augmentations = higher accuracy but slower"
            )
        else:
            num_augmentations = 1
        
        st.session_state['use_tta'] = use_tta
        st.session_state['num_augmentations'] = num_augmentations
        
        st.markdown("---")
        st.markdown("### 🎓 Thesis Project")
        st.info("Developed for FYDP on food classification using Deep learning")
        st.markdown("### 👥Team Members")
        st.info("Masud Rana Mamun & Momen Miah")
    # Check model availability
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, "model.pth")
    class_path = os.path.join(script_dir, "class_names.json")
    
    if not (os.path.exists(model_path) and os.path.exists(class_path)):
        st.error("⚠️ Model files not found! Please contact the administrator.")
        st.info(f"Looking for files in: {script_dir}")
        
        # Demo section
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="food-card">
                <h3>🍛 Biryani</h3>
                <p><strong>Origin:</strong> Dhaka, Old Dhaka</p>
                <p><strong>Calories:</strong> 290 kcal/100g</p>
                <p>Aromatic layered rice with meat</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="food-card">
                <h3>🐟 Hilsha Fish</h3>
                <p><strong>Origin:</strong> Padma River</p>
                <p><strong>Omega-3:</strong> Very High</p>
                <p>National fish of Bangladesh</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="food-card">
                <h3>🍜 Dal</h3>
                <p><strong>Origin:</strong> Universal</p>
                <p><strong>Protein:</strong> 8g/100g</p>
                <p>Daily staple lentil soup</p>
            </div>
            """, unsafe_allow_html=True)
        
        return
    
    # Load model silently
    try:
        model, class_names, detected_arch = load_model(model_path, class_path)
    except Exception as e:
        st.error(f"❌ Error loading model: {e}")
        return
    
    # Main content
    tab1, tab2 = st.tabs(["🔍 Classify Food", "📚 Food Database"])
    
    with tab1:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 📤 Upload Food Image")
            uploaded_image = st.file_uploader(
                "Choose an image...", 
                type=['jpg', 'jpeg', 'png', 'webp'],
                label_visibility="collapsed"
            )
            
            # Clear prediction if image is removed
            if uploaded_image is None and 'prediction' in st.session_state:
                del st.session_state['prediction']
            
            if uploaded_image:
                image = Image.open(uploaded_image).convert('RGB')
                st.image(image, caption="📸 Your uploaded image", use_container_width=True)
                
                if st.button("🔍 Analyze Food", type="primary", use_container_width=True):
                    use_tta = st.session_state.get('use_tta', True)
                    num_aug = st.session_state.get('num_augmentations', 5)
                    
                    status_text = "🧠 AI is analyzing with Test-Time Augmentation..." if use_tta else "🧠 AI is analyzing..."
                    with st.spinner(status_text):
                        progress_bar = st.progress(0)
                        for i in range(100):
                            time.sleep(0.015 if use_tta else 0.005)
                            progress_bar.progress(i + 1)
                        
                        predicted_class, confidence, top3 = predict_food(
                            image, model, class_names, 
                            use_tta=use_tta, 
                            num_augmentations=num_aug
                        )
                        progress_bar.empty()
                    
                    st.session_state['prediction'] = {
                        'class': predicted_class,
                        'confidence': confidence,
                        'top3': top3
                    }
                    st.rerun()
        
        with col2:
            st.markdown("### 📊 Analysis Results")
            
            if 'prediction' in st.session_state:
                pred = st.session_state['prediction']
                
                # Main prediction
                st.markdown(f"""
                <div class="prediction-badge">
                    🍽️ {pred['class'].replace('_', ' ').title()}
                </div>
                """, unsafe_allow_html=True)
                
                st.progress(pred['confidence'] / 100, text=f"Confidence: {pred['confidence']:.1f}%")
                
                # Top 3
                st.markdown("#### 🥇 Top 3 Predictions")
                for i, (food, conf) in enumerate(pred['top3'], 1):
                    emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
                    st.markdown(f"{emoji} **{food.replace('_', ' ').title()}**: {conf:.1f}%")
                
                # Nutrition
                nutrition = get_nutrition(pred['class'])
                
                st.markdown("---")
                st.markdown("### 🍴 Food Information")
                
                # Description and origin
                st.markdown(f"**📝 Description:** {nutrition['description']}")
                st.markdown(f"**🗺️ Origin:** {nutrition['origin']}")
                st.markdown(f"**⏰ Best Time:** {nutrition['best_time']}")
                
                st.markdown("---")
                st.markdown("### 📊 Nutrition Facts (per 100g)")
                
                # Nutrition metrics in grid
                met_col1, met_col2, met_col3, met_col4 = st.columns(4)
                met_col1.metric("🔥 Calories", f"{nutrition['calories']} kcal")
                met_col2.metric("🥩 Protein", f"{nutrition['protein']}g")
                met_col3.metric("🍚 Carbs", f"{nutrition['carbs']}g")
                met_col4.metric("🧈 Fat", f"{nutrition['fat']}g")
                
                st.markdown(f"**🥗 Fiber:** {nutrition['fiber']}g | **💊 Key Vitamins:** {nutrition['vitamins']}")
                st.info(f"**📏 Serving Size:** {nutrition['serving_size']}")
                
                st.markdown("---")
                st.markdown("### 👨‍🍳 How It's Made")
                st.markdown(f"<div class='info-section'>{nutrition['preparation']}</div>", unsafe_allow_html=True)
                
                st.markdown("### 💡 Health Tips")
                st.success(nutrition['health_tips'])
                
                st.markdown("### 🍽️ Popular Variants")
                st.markdown(f"_{nutrition['popular_variants']}_")
                
            else:
                st.info("👆 Upload an image and click 'Analyze Food' to see results")
    
    with tab2:
        st.markdown("### 📚 Complete Food Database")
        
        # Search
        search = st.text_input("🔍 Search food...", placeholder="e.g., biryani, fish, dal")
        
        # Filter foods
        foods_to_show = []
        for food_key, food_data in NUTRITION_DATA.items():
            if not search or search.lower() in food_key.lower() or search.lower() in food_data['description'].lower():
                foods_to_show.append((food_key, food_data))
        
        # Display in grid
        for i in range(0, len(foods_to_show), 2):
            col1, col2 = st.columns(2)
            
            for idx, col in enumerate([col1, col2]):
                if i + idx < len(foods_to_show):
                    food_key, food_data = foods_to_show[i + idx]
                    
                    with col:
                        with st.expander(f"🍽️ **{food_key.replace('_', ' ').title()}** - {food_data['calories']} kcal"):
                            st.markdown(f"**Description:** {food_data['description']}")
                            st.markdown(f"**Origin:** {food_data['origin']}")
                            st.markdown(f"**Protein:** {food_data['protein']}g | **Carbs:** {food_data['carbs']}g | **Fat:** {food_data['fat']}g")
                            st.markdown(f"**Health Tips:** {food_data['health_tips']}")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; padding: 20px; color: #666;'>
            Developed with ❤️ by <a href='https://github.com/MasudBinMazid' target='_blank' style='color: #FF6B6B; text-decoration: none;'>Masud</a>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
