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
    page_title="Bangladeshi Food Classifier",
    page_icon="🍕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Clean, responsive design
st.markdown("""
<style>
    /* Dark theme */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }
    
    /* Text colors */
    .stApp, .stMarkdown, p, span, div, label {
        color: #e0e0e0 !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    
    /* Hide branding */
    #MainMenu, footer, header {visibility: hidden;}
    
    
    /* Sidebar - Always visible */
    section[data-testid="stSidebar"] {
        background: rgba(20, 20, 40, 0.98) !important;
        border-right: 1px solid rgba(102, 126, 234, 0.3) !important;
    }
    
    section[data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }
    
    section[data-testid="stSidebar"] h3 {
        color: #667eea !important;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 600 !important;
        border: none !important;
        width: 100%;
    }
    
    .stButton>button:hover {
        opacity: 0.9;
        transform: translateY(-1px);
    }
    
    /* File Uploader */
    .stFileUploader {
        background: rgba(135, 206, 235, 0.15);
        border: 2px dashed rgba(135, 206, 235, 0.6);
        border-radius: 10px;
        padding: 1rem;
    }
    
    .stFileUploader:hover {
        background: rgba(135, 206, 235, 0.25);
        border-color: #87CEEB;
    }
    
    .stFileUploader label, .stFileUploader p, .stFileUploader span {
        color: #000000 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #b0b0b0 !important;
        padding: 0.5rem 1rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #667eea !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #b0b0b0 !important;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Responsive - Mobile */
    @media (max-width: 768px) {
        .block-container {
            padding: 1rem !important;
        }
        
        .stButton>button {
            padding: 0.5rem 1rem !important;
        }
    }
    
    /* Container max-width */
    .block-container {
        max-width: 1400px !important;
        padding: 2rem !important;
    }
    
    @media (max-width: 480px) {
        .main-header {
            padding: 1rem;
        }
        
        .main-header h1 {
            font-size: 1.5rem;
        }
        
        .main-header p {
            font-size: 0.9rem;
        }
        
        .stButton>button {
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
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

<!-- PWA Manifest Link -->
<link rel="manifest" href="/app/static/manifest.json">

<!-- PWA Meta Tags -->
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Food Classifier">
<meta name="theme-color" content="#667eea">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">

<!-- PWA Icons -->
<link rel="icon" type="image/png" sizes="192x192" href="/app/static/icon-192.png">
<link rel="apple-touch-icon" sizes="192x192" href="/app/static/icon-192.png">

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
# COMPREHENSIVE NUTRITION DATABASE FOR 33 BANGLADESHI FOODS
# ============================================
NUTRITION_DATA = {
    "alu_vorta": {
        "calories": 95, "protein": 2.1, "carbs": 18.5, "fat": 2.5, "fiber": 2.3,
        "description": "Mashed potato with mustard oil, green chilies, onions, and coriander",
        "origin": "Popular across Bangladesh, especially in rural areas",
        "preparation": "Boil potatoes until soft, mash them, and mix with mustard oil, green chilies, onions, salt, and coriander leaves. Some add garlic for extra flavor.",
        "best_time": "Lunch or dinner as side dish",
        "health_tips": [
            "✓ Good source of vitamin C and potassium",
            "✓ Low in calories, suitable for weight management",
            "✓ Mustard oil provides healthy omega-3 fatty acids",
            "Avoid excessive oil to keep it heart-healthy"
        ],
        "vitamins": "Vitamin C, Potassium, Omega-3",
        "serving_size": "100g",
        "popular_variants": "Plain Alu Vorta, with Garlic, with Egg"
    },
    "bakorkhani": {
        "calories": 385, "protein": 8.5, "carbs": 58.0, "fat": 13.0, "fiber": 2.1,
        "description": "Thick, crispy flatbread made from refined flour, ghee, milk, and sugar",
        "origin": "Old Dhaka specialty, popular during Ramadan",
        "preparation": "Made from refined flour, ghee, milk, and sugar. Dough is layered with ghee, rolled thin, and baked in a clay oven (tandoor) until crispy and flaky.",
        "best_time": "Iftar during Ramadan, breakfast with tea",
        "health_tips": [
            "⚠️ High in calories and carbs - consume in moderation",
            "⚠️ Contains saturated fat from ghee",
            "Best paired with tea and enjoyed occasionally",
            "Good energy source for breaking fast during Ramadan"
        ],
        "vitamins": "B vitamins, Iron",
        "serving_size": "100g",
        "popular_variants": "Sweet Bakorkhani, Savory Bakorkhani"
    },
    "bhapa": {
        "calories": 245, "protein": 18.5, "carbs": 8.2, "fat": 16.0, "fiber": 1.2,
        "description": "Steamed fish in mustard paste - traditional delicacy",
        "origin": "Traditional across Bangladesh, especially Sylhet",
        "preparation": "Fish (typically hilsa or rui) marinated with mustard paste, green chilies, turmeric, and salt, then steamed in banana leaves or aluminum foil.",
        "best_time": "Lunch or dinner",
        "health_tips": [
            "✓ Excellent source of protein and omega-3 fatty acids",
            "✓ Steaming preserves nutrients better than frying",
            "✓ Mustard has anti-inflammatory properties",
            "Low in carbs, suitable for diabetics"
        ],
        "vitamins": "Omega-3, Protein, Vitamin D, Selenium",
        "serving_size": "100g",
        "popular_variants": "Ilish Bhapa, Rui Bhapa, Pabda Bhapa"
    },
    "burger": {
        "calories": 295, "protein": 17.0, "carbs": 24.0, "fat": 14.0, "fiber": 1.5,
        "description": "Grilled or fried patty in a bun with vegetables and sauces",
        "origin": "Urban areas, popular fast food in Dhaka and Chittagong",
        "preparation": "Grilled or fried beef/chicken patty served in a bun with lettuce, tomato, onion, cheese, and sauces. Local variations include spicy chicken and beef burgers.",
        "best_time": "Snacks, lunch, dinner",
        "health_tips": [
            "⚠️ High in calories and saturated fat",
            "Choose grilled over fried patties",
            "Add more vegetables for fiber",
            "Limit consumption to occasional treats"
        ],
        "vitamins": "B vitamins, Iron, Protein",
        "serving_size": "100g",
        "popular_variants": "Chicken Burger, Beef Burger, Veggie Burger"
    },
    "chicken": {
        "calories": 165, "protein": 31.0, "carbs": 0.0, "fat": 3.6, "fiber": 0.0,
        "description": "Versatile poultry - prepared in various ways",
        "origin": "Widely consumed across Bangladesh",
        "preparation": "Can be prepared in various ways - curry, roasted, fried, or grilled. Common preparation includes cooking with onions, garlic, ginger, and spices.",
        "best_time": "Any meal",
        "health_tips": [
            "✓ Excellent lean protein source",
            "✓ Low in fat when skinless",
            "✓ Rich in vitamins B6 and B12",
            "Choose grilled or boiled over fried preparations"
        ],
        "vitamins": "B6, B12, Niacin, Selenium, Phosphorus",
        "serving_size": "100g",
        "popular_variants": "Chicken Curry, Roast, Grilled, Fried"
    },
    "chicken_roast": {
        "calories": 280, "protein": 26.5, "carbs": 5.5, "fat": 17.0, "fiber": 0.8,
        "description": "Deep-fried chicken in rich spiced gravy with potatoes and eggs",
        "origin": "Popular in Dhaka and urban areas, wedding/party dish",
        "preparation": "Chicken marinated in yogurt, ginger-garlic paste, and spices, then deep-fried and cooked in a rich gravy with potatoes, eggs, and aromatic spices.",
        "best_time": "Special occasions, parties, weddings",
        "health_tips": [
            "⚠️ High in calories and fat due to frying",
            "✓ Good protein content",
            "Consume in moderation",
            "Remove excess oil before eating"
        ],
        "vitamins": "B vitamins, Iron, Protein",
        "serving_size": "100g",
        "popular_variants": "Spicy Roast, Mild Roast, Hotel Style"
    },
    "chingri_vuna": {
        "calories": 195, "protein": 24.0, "carbs": 6.5, "fat": 8.5, "fiber": 1.5,
        "description": "Prawns sautéed with spices in thick masala",
        "origin": "Coastal areas - Khulna, Barisal, Chittagong",
        "preparation": "Prawns sautéed with onions, garlic, ginger, tomatoes, and spices in mustard oil. Cooked until the masala thickens and coats the prawns.",
        "best_time": "Lunch or dinner",
        "health_tips": [
            "✓ Excellent source of protein and omega-3",
            "✓ Rich in selenium and vitamin B12",
            "✓ Low in carbohydrates",
            "⚠️ High in cholesterol - consume moderately if at risk"
        ],
        "vitamins": "Omega-3, B12, Selenium, Protein",
        "serving_size": "100g",
        "popular_variants": "Bagda Chingri, Galda Chingri, Chingri Malai"
    },
    "chomchom": {
        "calories": 350, "protein": 6.5, "carbs": 52.0, "fat": 13.0, "fiber": 0.2,
        "description": "Oval-shaped cottage cheese sweet soaked in sugar syrup",
        "origin": "Tangail and Porabari are famous for authentic Chomchom",
        "preparation": "Made from chhana (cottage cheese) mixed with semolina, shaped into ovals, and soaked in sugar syrup flavored with cardamom and rose water.",
        "best_time": "Dessert, festivals, celebrations",
        "health_tips": [
            "⚠️ Very high in sugar and calories",
            "⚠️ Not suitable for diabetics",
            "Consume as an occasional treat only",
            "Contains some protein from milk"
        ],
        "vitamins": "Calcium, Protein",
        "serving_size": "100g",
        "popular_variants": "Tangail Chomchom, Porabari Chomchom"
    },
    "chowmein": {
        "calories": 198, "protein": 6.5, "carbs": 28.5, "fat": 6.8, "fiber": 2.4,
        "description": "Stir-fried noodles with vegetables and meat",
        "origin": "Popular street food in Dhaka, Chittagong, and Sylhet",
        "preparation": "Stir-fried noodles with vegetables (cabbage, carrots, capsicum), chicken or egg, and soy sauce. Cooked on high heat in a wok.",
        "best_time": "Lunch, dinner, snacks",
        "health_tips": [
            "✓ Moderate calorie content",
            "✓ Contains vegetables providing vitamins",
            "Choose whole wheat noodles for more fiber",
            "Control oil quantity to reduce fat"
        ],
        "vitamins": "B vitamins, Vitamin A, Iron",
        "serving_size": "100g",
        "popular_variants": "Chicken Chowmein, Vegetable Chowmein, Egg Chowmein"
    },
    "dal": {
        "calories": 116, "protein": 9.0, "carbs": 20.0, "fat": 0.5, "fiber": 7.9,
        "description": "Lentil soup - the heart of Bengali meals, cooked with turmeric and spices",
        "origin": "Staple food across all regions of Bangladesh",
        "preparation": "Lentils boiled with turmeric and salt, then tempered with onions, garlic, and spices fried in oil. Common varieties include masoor, moong, and chana dal.",
        "best_time": "Every meal - breakfast, lunch, dinner",
        "health_tips": [
            "✓ Excellent plant-based protein source",
            "✓ High in fiber, aids digestion",
            "✓ Rich in iron and folate",
            "✓ Low in fat and calories",
            "Perfect for vegetarians and weight management"
        ],
        "vitamins": "Folate, Iron, Magnesium, Potassium, Zinc",
        "serving_size": "100g",
        "popular_variants": "Masoor Dal, Moong Dal, Chana Dal, Mixed Dal"
    },
    "egg_curry": {
        "calories": 185, "protein": 11.5, "carbs": 8.5, "fat": 12.0, "fiber": 2.1,
        "description": "Hard-boiled eggs in spiced tomato-onion gravy",
        "origin": "Popular across Bangladesh, especially as a breakfast item",
        "preparation": "Boiled eggs cooked in onion-tomato gravy with ginger, garlic, and spices (turmeric, cumin, coriander, chili powder). Often garnished with coriander leaves.",
        "best_time": "Any meal - common breakfast with paratha",
        "health_tips": [
            "✓ Good source of complete protein",
            "✓ Contains vitamins A, D, E, and B12",
            "✓ Affordable protein option",
            "⚠️ Moderate fat content - control oil quantity"
        ],
        "vitamins": "B12, D, A, Choline, Selenium",
        "serving_size": "100g",
        "popular_variants": "Dim Bhuna, Dimer Dalna, Egg Masala"
    },
    "french_fries": {
        "calories": 312, "protein": 3.4, "carbs": 41.0, "fat": 15.0, "fiber": 3.8,
        "description": "Deep-fried potato strips",
        "origin": "Urban fast food centers across Bangladesh",
        "preparation": "Potatoes cut into strips and deep-fried until golden and crispy. Often seasoned with salt and served with ketchup or mayonnaise.",
        "best_time": "Snacks",
        "health_tips": [
            "⚠️ High in calories and unhealthy fats",
            "⚠️ Deep-fried, increases trans fat content",
            "Contains acrylamide when overcooked",
            "Limit consumption to occasional treats",
            "Baked version is a healthier alternative"
        ],
        "vitamins": "Potassium, Vitamin C",
        "serving_size": "100g",
        "popular_variants": "Crispy Fries, Curly Fries, Wedges"
    },
    "fried_chicken": {
        "calories": 320, "protein": 24.0, "carbs": 12.5, "fat": 20.0, "fiber": 0.8,
        "description": "Crispy battered and deep-fried chicken",
        "origin": "Popular fast food in Dhaka, Chittagong, and Sylhet",
        "preparation": "Chicken pieces marinated in spices, coated with flour batter, and deep-fried until crispy. Local versions include spicy marinades with chili and garlic.",
        "best_time": "Lunch, dinner, snacks",
        "health_tips": [
            "⚠️ Very high in calories and fat",
            "✓ Good protein content",
            "Remove skin to reduce fat",
            "Consume rarely, choose grilled alternatives",
            "High sodium content"
        ],
        "vitamins": "B vitamins, Protein",
        "serving_size": "100g",
        "popular_variants": "Spicy Fried Chicken, Crispy Chicken, Wings"
    },
    "fuchka": {
        "calories": 125, "protein": 3.8, "carbs": 22.0, "fat": 2.5, "fiber": 2.8,
        "description": "Crispy hollow puris with spiced tamarind water",
        "origin": "Street food popular everywhere, especially Dhaka and Chittagong",
        "preparation": "Crispy hollow puris filled with spiced tamarind water, boiled chickpeas, potatoes, onions, and coriander. The tangy, spicy water is the key element.",
        "best_time": "Evening snacks",
        "health_tips": [
            "✓ Relatively low in calories",
            "⚠️ Hygiene concerns with street vendors",
            "Ensure clean water is used",
            "Good source of carbs for energy",
            "Tamarind aids digestion"
        ],
        "vitamins": "Vitamin C, Iron",
        "serving_size": "100g",
        "popular_variants": "Fuchka, Puchka, Golgappa"
    },
    "jalebi": {
        "calories": 425, "protein": 3.5, "carbs": 65.0, "fat": 16.0, "fiber": 0.5,
        "description": "Deep-fried spiral-shaped sweet soaked in sugar syrup",
        "origin": "Popular sweet across Bangladesh, especially during festivals",
        "preparation": "Batter made from refined flour fermented overnight, then piped in circular shapes into hot oil and deep-fried. Immediately soaked in sugar syrup flavored with cardamom and saffron.",
        "best_time": "Special occasions, festivals, weddings",
        "health_tips": [
            "⚠️ Extremely high in sugar and calories",
            "⚠️ Deep-fried, high in unhealthy fats",
            "⚠️ Not suitable for diabetics",
            "Consume only on special occasions",
            "Can cause blood sugar spikes"
        ],
        "vitamins": "Minimal nutritional value",
        "serving_size": "100g",
        "popular_variants": "Crispy Jalebi, Paneer Jalebi, Imarti"
    },
    "jhalmuri": {
        "calories": 280, "protein": 6.5, "carbs": 52.0, "fat": 5.5, "fiber": 4.2,
        "description": "Spicy puffed rice snack with vegetables and peanuts",
        "origin": "Popular street snack in Dhaka, Chittagong, and all urban areas",
        "preparation": "Puffed rice mixed with chopped onions, tomatoes, green chilies, mustard oil, chanachur, peanuts, and coriander. Seasoned with salt and lime juice.",
        "best_time": "Evening snacks",
        "health_tips": [
            "✓ Low in fat and calories",
            "✓ Good source of fiber",
            "✓ Contains vegetables and peanuts",
            "⚠️ Watch portion size as it's easy to overeat",
            "Nutritious evening snack option"
        ],
        "vitamins": "Vitamin C, Iron, Fiber",
        "serving_size": "100g",
        "popular_variants": "Masala Muri, Chanachur Muri"
    },
    "kotkoti": {
        "calories": 405, "protein": 7.2, "carbs": 48.0, "fat": 21.0, "fiber": 1.8,
        "description": "Traditional Bengali sweet made from dried milk and sugar",
        "origin": "Traditional Bengali sweet from Murshidabad and Dhaka",
        "preparation": "Made from khoya (dried milk), sugar, and ghee. Mixture is cooked until thick, shaped into round balls, and garnished with nuts or coconut.",
        "best_time": "Dessert, festivals",
        "health_tips": [
            "⚠️ Very high in calories and fat",
            "⚠️ High sugar content",
            "Contains some calcium from milk",
            "Consume sparingly as a festive treat",
            "Not suitable for weight loss diets"
        ],
        "vitamins": "Calcium, Protein",
        "serving_size": "100g",
        "popular_variants": "Milk Kotkoti, Khoya Sweets"
    },
    "morog_polao": {
        "calories": 215, "protein": 12.5, "carbs": 28.0, "fat": 6.5, "fiber": 1.2,
        "description": "Fragrant rice cooked with chicken and aromatic spices",
        "origin": "Wedding and festive dish, popular in Dhaka and Old Bengal regions",
        "preparation": "Basmati rice cooked with chicken, ghee, yogurt, onions, and aromatic spices (cinnamon, cardamom, bay leaves, cloves). Chicken is first marinated and then layered with rice.",
        "best_time": "Special occasions, weddings, lunch",
        "health_tips": [
            "✓ Balanced meal with protein and carbs",
            "✓ Aromatic spices aid digestion",
            "⚠️ Moderate fat due to ghee",
            "Control portion size",
            "Good source of energy for special occasions"
        ],
        "vitamins": "B vitamins, Iron, Protein",
        "serving_size": "100g",
        "popular_variants": "Morog Polao, Chicken Polao"
    },
    "mutton_leg_roast": {
        "calories": 340, "protein": 26.0, "carbs": 8.5, "fat": 23.0, "fiber": 1.5,
        "description": "Slow-roasted mutton leg in rich spiced gravy",
        "origin": "Special occasion dish in Dhaka and urban areas",
        "preparation": "Mutton leg marinated with yogurt, spices, and herbs, then slow-roasted or pressure-cooked. Finished with fried onions, boiled eggs, and potatoes in a rich gravy.",
        "best_time": "Special occasions, weddings, celebrations",
        "health_tips": [
            "⚠️ High in calories and saturated fat",
            "✓ Excellent protein source",
            "✓ Rich in iron and zinc",
            "Consume in small portions",
            "Remove visible fat before eating"
        ],
        "vitamins": "B12, Iron, Zinc, Protein",
        "serving_size": "100g",
        "popular_variants": "Slow Roast, Pressure Cooked, Oven Roasted"
    },
    "paratha": {
        "calories": 320, "protein": 6.8, "carbs": 42.0, "fat": 14.0, "fiber": 2.2,
        "description": "Layered flatbread with oil or ghee",
        "origin": "Popular breakfast item across Bangladesh",
        "preparation": "Wheat flour dough layered with oil or ghee, rolled thin, and cooked on a griddle until golden and flaky. Can be plain or stuffed with vegetables, eggs, or meat.",
        "best_time": "Breakfast",
        "health_tips": [
            "⚠️ High in calories and fat",
            "✓ Provides energy for the day",
            "Whole wheat version is healthier",
            "Pair with vegetables for balanced nutrition",
            "Control oil quantity during cooking"
        ],
        "vitamins": "B vitamins, Iron, Magnesium",
        "serving_size": "100g",
        "popular_variants": "Plain Paratha, Aloo Paratha, Egg Paratha, Mughlai Paratha"
    },
    "pera_sondesh": {
        "calories": 365, "protein": 8.5, "carbs": 55.0, "fat": 12.0, "fiber": 0.3,
        "description": "Soft cottage cheese sweet shaped into rounds",
        "origin": "Originated in West Bengal, popular in Dhaka and across Bangladesh",
        "preparation": "Chhana (cottage cheese) kneaded with sugar and cooked until thick. Shaped into small round sweets and garnished with nuts or cardamom.",
        "best_time": "Dessert, festivals",
        "health_tips": [
            "⚠️ High in sugar and calories",
            "✓ Contains protein from milk",
            "✓ Source of calcium",
            "Consume in moderation",
            "Better than deep-fried sweets"
        ],
        "vitamins": "Calcium, Protein",
        "serving_size": "100g",
        "popular_variants": "Sandesh, Kachagolla, Nolen Gurer Sandesh"
    },
    "peyaju": {
        "calories": 285, "protein": 6.2, "carbs": 35.0, "fat": 13.0, "fiber": 3.5,
        "description": "Onion and lentil fritters",
        "origin": "Popular iftar item during Ramadan, common across Bangladesh",
        "preparation": "Sliced onions mixed with lentils (dal), rice flour, spices, and green chilies, formed into fritters and deep-fried until crispy.",
        "best_time": "Iftar, evening snacks",
        "health_tips": [
            "⚠️ Deep-fried, high in calories",
            "✓ Contains onions with antioxidants",
            "✓ Lentils provide protein",
            "Drain excess oil before eating",
            "Good energy source for breaking fast"
        ],
        "vitamins": "Protein, Fiber, Iron",
        "serving_size": "100g",
        "popular_variants": "Onion Peyaju, Mixed Dal Peyaju"
    },
    "pizza": {
        "calories": 285, "protein": 12.0, "carbs": 36.0, "fat": 10.0, "fiber": 2.3,
        "description": "Baked dough base with cheese, sauce, and toppings",
        "origin": "Urban fast food centers, popular in Dhaka and Chittagong",
        "preparation": "Dough base topped with tomato sauce, cheese, and various toppings (vegetables, chicken, beef), baked in an oven until cheese melts and crust is crispy.",
        "best_time": "Lunch, dinner, parties",
        "health_tips": [
            "⚠️ High in calories and sodium",
            "✓ Contains calcium from cheese",
            "Choose thin crust and more vegetables",
            "Limit cheese and processed meats",
            "Consume occasionally"
        ],
        "vitamins": "Calcium, Protein, B vitamins",
        "serving_size": "100g",
        "popular_variants": "Margherita, Pepperoni, Chicken Pizza, Veggie Pizza"
    },
    "puli_pitha": {
        "calories": 265, "protein": 5.8, "carbs": 45.0, "fat": 7.5, "fiber": 2.1,
        "description": "Rice flour dumplings with sweet coconut filling",
        "origin": "Traditional winter dessert across rural and urban Bangladesh",
        "preparation": "Rice flour dough shaped into dumplings, filled with sweet coconut and jaggery mixture, then steamed or boiled in sweetened milk.",
        "best_time": "Winter season, dessert",
        "health_tips": [
            "✓ Steamed, not fried - healthier option",
            "✓ Contains coconut with healthy fats",
            "⚠️ High in sugar from jaggery",
            "Traditional winter comfort food",
            "Good source of quick energy"
        ],
        "vitamins": "Iron (from jaggery), Fiber",
        "serving_size": "100g",
        "popular_variants": "Dudh Puli, Chitoi Pitha, Patishapta"
    },
    "rice": {
        "calories": 130, "protein": 2.7, "carbs": 28.0, "fat": 0.3, "fiber": 0.4,
        "description": "Staple grain of Bangladesh",
        "origin": "Staple food across entire Bangladesh",
        "preparation": "Rice grains washed and boiled in water until soft. Can be cooked plain or with salt. Brown rice is also becoming popular.",
        "best_time": "Every meal - breakfast, lunch, dinner",
        "health_tips": [
            "✓ Primary energy source",
            "✓ Gluten-free grain",
            "✓ Easy to digest",
            "Choose brown rice for more fiber",
            "Control portion size for weight management",
            "Pair with dal and vegetables for balanced meal"
        ],
        "vitamins": "B vitamins, Manganese",
        "serving_size": "100g",
        "popular_variants": "White Rice, Brown Rice, Basmati Rice"
    },
    "roshmalai": {
        "calories": 340, "protein": 7.5, "carbs": 48.0, "fat": 14.0, "fiber": 0.2,
        "description": "Soft cheese patties in sweetened, thickened milk with cardamom",
        "origin": "Comilla is famous for authentic Roshmalai",
        "preparation": "Chhana (cottage cheese) shaped into flat discs, boiled in sugar syrup, then soaked in sweetened, cardamom-flavored condensed milk. Garnished with pistachios.",
        "best_time": "Dessert, special occasions, Eid",
        "health_tips": [
            "⚠️ Very high in sugar and calories",
            "✓ Contains protein and calcium from milk",
            "⚠️ High in saturated fat",
            "Consume as an occasional dessert",
            "Not suitable for diabetics"
        ],
        "vitamins": "Calcium, Protein, Vitamin D, B12",
        "serving_size": "100g",
        "popular_variants": "Rasgulla, Chamcham, Comilla Roshmalai"
    },
    "rupchanda_fry": {
        "calories": 245, "protein": 22.0, "carbs": 8.5, "fat": 14.0, "fiber": 0.8,
        "description": "Fried pomfret fish",
        "origin": "Popular in coastal regions and urban restaurants",
        "preparation": "Pomfret fish marinated with turmeric, chili powder, salt, and lemon juice, coated with flour or semolina, and shallow or deep-fried until golden and crispy.",
        "best_time": "Lunch or dinner",
        "health_tips": [
            "✓ Excellent source of protein",
            "✓ Rich in omega-3 fatty acids",
            "✓ Contains vitamin D and selenium",
            "⚠️ Frying increases calorie content",
            "Choose shallow frying over deep frying"
        ],
        "vitamins": "Omega-3, Vitamin D, Selenium, B12",
        "serving_size": "100g",
        "popular_variants": "Pomfret Fry, Silver Pomfret"
    },
    "shami_kabab": {
        "calories": 255, "protein": 18.5, "carbs": 12.0, "fat": 15.0, "fiber": 2.5,
        "description": "Minced meat patties with chana dal",
        "origin": "Mughlai dish popular in Dhaka, especially Old Dhaka",
        "preparation": "Minced meat (beef or mutton) cooked with chana dal, onions, ginger, garlic, and spices until soft. Mashed, shaped into patties, and shallow-fried.",
        "best_time": "Snacks, iftar, dinner appetizer",
        "health_tips": [
            "✓ High protein content",
            "✓ Contains dal providing fiber",
            "⚠️ Moderate to high fat content",
            "Good source of iron and zinc",
            "Choose lean meat to reduce fat"
        ],
        "vitamins": "B12, B6, Iron, Zinc, Protein",
        "serving_size": "100g",
        "popular_variants": "Shami Kabab, Chapli Kabab, Seekh Kabab"
    },
    "shawarma": {
        "calories": 265, "protein": 16.5, "carbs": 22.0, "fat": 12.0, "fiber": 2.8,
        "description": "Grilled meat wrapped in flatbread with vegetables",
        "origin": "Popular street and fast food in Dhaka and Chittagong",
        "preparation": "Marinated chicken or beef grilled on a vertical rotisserie, thinly sliced, and wrapped in flatbread with vegetables, pickles, and garlic sauce or tahini.",
        "best_time": "Lunch, dinner, snacks",
        "health_tips": [
            "✓ Good protein source",
            "✓ Contains vegetables",
            "⚠️ Sauces add extra calories",
            "Choose chicken over beef for less fat",
            "Request less sauce to reduce calories"
        ],
        "vitamins": "B vitamins, Protein, Fiber",
        "serving_size": "100g",
        "popular_variants": "Chicken Shawarma, Beef Shawarma, Mixed Shawarma"
    },
    "shorshe_ilish": {
        "calories": 310, "protein": 20.5, "carbs": 4.5, "fat": 24.0, "fiber": 1.5,
        "description": "Hilsa fish cooked in mustard sauce - National dish",
        "origin": "National dish of Bangladesh, especially popular in rainy season",
        "preparation": "Hilsa fish cooked in mustard paste gravy with green chilies, turmeric, and mustard oil. The mustard paste is the key ingredient giving the dish its signature flavor.",
        "best_time": "Lunch or dinner, especially during monsoon",
        "health_tips": [
            "✓ Extremely rich in omega-3 fatty acids",
            "✓ Excellent protein source",
            "✓ Mustard has anti-inflammatory properties",
            "✓ Good for heart health",
            "⚠️ High in fat (healthy fats)",
            "Contains small bones - eat carefully"
        ],
        "vitamins": "Omega-3, Vitamin D, B12, Selenium",
        "serving_size": "100g",
        "popular_variants": "Shorshe Ilish, Ilish Bhapa, Ilish Bhaja"
    },
    "singara": {
        "calories": 262, "protein": 5.5, "carbs": 32.0, "fat": 12.5, "fiber": 3.2,
        "description": "Triangular fried pastry with spiced potato filling",
        "origin": "Popular snack across Bangladesh, especially as tea-time snack",
        "preparation": "Triangular pastry filled with spiced potatoes, peas, onions, and sometimes minced meat. Deep-fried until golden and crispy.",
        "best_time": "Evening snack with tea",
        "health_tips": [
            "⚠️ Deep-fried, high in calories",
            "✓ Contains vegetables providing fiber",
            "Drain excess oil before eating",
            "Baked version is a healthier option",
            "Popular tea-time snack in moderation"
        ],
        "vitamins": "Vitamin C, B vitamins, Potassium",
        "serving_size": "100g",
        "popular_variants": "Aloo Shingara, Beef Shingara, Mixed Shingara"
    },
    "tea": {
        "calories": 35, "protein": 0.5, "carbs": 7.0, "fat": 1.2, "fiber": 0.0,
        "description": "Most popular beverage in Bangladesh",
        "origin": "Most popular beverage across all regions of Bangladesh",
        "preparation": "Black tea leaves boiled with water, milk, and sugar. Some add ginger, cardamom, or cinnamon for flavor. Sylhet region is famous for seven-layer tea.",
        "best_time": "Any time - morning, afternoon, evening",
        "health_tips": [
            "✓ Contains antioxidants from tea leaves",
            "✓ May boost metabolism",
            "⚠️ Excess sugar adds empty calories",
            "Reduce sugar for health benefits",
            "Green tea is a healthier alternative",
            "Limit to 2-3 cups daily"
        ],
        "vitamins": "Antioxidants, Caffeine",
        "serving_size": "100ml (with milk and sugar)",
        "popular_variants": "Black Tea, Milk Tea, Seven-Layer Tea, Green Tea"
    },
    "tikka": {
        "calories": 220, "protein": 24.0, "carbs": 6.5, "fat": 11.0, "fiber": 1.2,
        "description": "Grilled marinated chicken pieces",
        "origin": "Popular appetizer in restaurants across Bangladesh",
        "preparation": "Chicken pieces marinated in yogurt, lemon juice, ginger-garlic paste, and spices (cumin, coriander, garam masala), then grilled or baked in a tandoor oven.",
        "best_time": "Appetizer, snacks, dinner",
        "health_tips": [
            "✓ High protein, low carb option",
            "✓ Grilled/baked, not fried - healthier",
            "✓ Yogurt marinade aids digestion",
            "✓ Good for muscle building",
            "Excellent choice for weight management"
        ],
        "vitamins": "B vitamins, Protein, Selenium",
        "serving_size": "100g",
        "popular_variants": "Chicken Tikka, Tikka Masala, Tandoori Tikka"
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

def predict_food(image, model, class_names, use_tta=True, num_augmentations=5, confidence_threshold=60.0):
    """Predict food class from image with Test-Time Augmentation (TTA) and confidence validation
    
    Args:
        image: PIL Image
        model: PyTorch model
        class_names: List of class names
        use_tta: Whether to use test-time augmentation (default: True)
        num_augmentations: Number of augmentations for TTA (default: 5)
        confidence_threshold: Minimum confidence to accept prediction (default: 50.0%)
    
    Returns:
        predicted_class: str - Predicted food class or "UNKNOWN"
        confidence_score: float - Confidence percentage
        top3: list - Top 3 predictions with confidence
        is_valid: bool - Whether prediction meets confidence threshold
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
    
    # Validate prediction confidence
    is_valid = confidence_score >= confidence_threshold
    if not is_valid:
        predicted_class = "UNKNOWN"
    
    return predicted_class, confidence_score, top3, is_valid

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
        "health_tips": ["Nutrition information not available in database", "Enjoy in moderation as part of a balanced diet"],
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
    <div style='background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); 
                border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding: 2rem; 
                text-align: center; margin-bottom: 2rem; border-radius: 15px;'>
        <h1 style='color: #ffffff; margin-bottom: 0.5rem;'>Bangladeshi Food Classifier</h1>
        <p style='color: #b0b0b0; margin: 0; font-size: 1.1rem;'>AI-Powered Food Recognition & Nutrition Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🍽️ Food AI")
        st.markdown("*Powered by Deep Learning*")
        
        st.markdown("### 📊 Features")
        st.markdown("""
        - 🔍 Identify **35+ Bangladeshi dishes**
        - 📊 Detailed **nutrition facts**
        - 🗺️ Regional **origins & history**
        - 👨‍🍳 Traditional **preparation methods**
        - 💡 Personalized **health tips**
        - 🎯 **97%+ accuracy** with TTA
        """)
        
        st.markdown("---")
        st.markdown("### ⚙️ Settings")
        
        st.info("📸 **Multi-Image Mode**: Upload 2-5 images from different angles for higher accuracy!")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        use_tta = st.checkbox(
            "🔄 Enable Test-Time Augmentation (TTA)",
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
        st.markdown("### 🎯 Confidence Settings")
        
        st.markdown("""
        Set minimum confidence level for predictions. Higher values make the model more strict.
        - **Low (30-50%)**: Accept more predictions, may include uncertain results
        - **Medium (50-70%)**: Balanced - **Recommended**
        - **High (70-90%)**: Very strict, only high-confidence predictions
        """)
        
        confidence_threshold = st.slider(
            "Minimum Confidence Level (%)",
            min_value=30.0,
            max_value=90.0,
            value=60.0,
            step=5.0,
            help="Predictions below this confidence will be marked as 'Low Confidence'. Recommended: 60%"
        )
        st.session_state['confidence_threshold'] = confidence_threshold
        
        # Show current setting
        if confidence_threshold < 50:
            st.warning(f"⚠️ Current: **{confidence_threshold:.0f}%** - Low threshold (More permissive)")
        elif confidence_threshold <= 70:
            st.success(f"✅ Current: **{confidence_threshold:.0f}%** - Medium threshold (Recommended)")
        else:
            st.info(f"🔒 Current: **{confidence_threshold:.0f}%** - High threshold (Very strict)")
        
        st.caption(f"Current: {confidence_threshold:.0f}% - Predictions below this will be marked as 'Out of Range'")
        
        st.markdown("---")
        st.markdown("### 📱 Install as App")
        st.markdown("""
        **Mobile (Android/iOS):**  
        Tap browser menu → "Add to Home Screen"
        
        **Desktop (Chrome/Edge):**  
        Click ⊕ icon in address bar
        """)
        
        if st.button("📲 View Install Guide", use_container_width=True):
            st.info("""
            **Android Chrome/Samsung:**
            1. Tap ⋮ menu
            2. Tap "Install app"
            3. Tap "Install"
            
            **iPhone Safari:**
            1. Tap Share □↑
            2. Scroll down
            3. Tap "Add to Home Screen"
            4. Tap "Add"
            
            **Desktop:**
            1. Look for ⊕ in address bar
            2. Or: Settings → "Install app"
            """)
        
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
            st.markdown("### Upload Food Image(s)")
            
            # Toggle for multi-image mode
            multi_image_mode = st.checkbox(
                "📸 Multi-Image Mode",
                value=False,
                help="Upload 2-5 images from different angles for better accuracy"
            )
            
            if multi_image_mode:
                uploaded_images = st.file_uploader(
                    "Choose 2-5 images of the same food from different angles...", 
                    type=['jpg', 'jpeg', 'png', 'webp'],
                    accept_multiple_files=True,
                    label_visibility="collapsed"
                )
                
                # Clear prediction if images are removed
                if not uploaded_images and 'prediction' in st.session_state:
                    del st.session_state['prediction']
                
                if uploaded_images:
                    if len(uploaded_images) > 5:
                        st.warning("⚠️ Please upload maximum 5 images. Using first 5 images only.")
                        uploaded_images = uploaded_images[:5]
                    
                    # Display all uploaded images in a grid
                    st.markdown(f"**{len(uploaded_images)} image(s) uploaded:**")
                    cols = st.columns(min(len(uploaded_images), 3))
                    for idx, img_file in enumerate(uploaded_images):
                        with cols[idx % 3]:
                            img = Image.open(img_file).convert('RGB')
                            st.image(img, caption=f"Image {idx+1}", use_container_width=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Confidence level selector for multi-image mode
                    st.markdown("### 🎯 Set Confidence Level")
                    confidence_threshold = st.slider(
                        "Choose minimum confidence level for prediction",
                        min_value=30.0,
                        max_value=90.0,
                        value=st.session_state.get('confidence_threshold', 60.0),
                        step=5.0,
                        help="Higher values make the model more strict. Recommended: 60%",
                        key="multi_confidence"
                    )
                    st.session_state['confidence_threshold'] = confidence_threshold
                    
                    # Visual feedback
                    if confidence_threshold < 50:
                        st.warning(f"⚠️ **{confidence_threshold:.0f}%** - Low threshold (More permissive)")
                    elif confidence_threshold <= 70:
                        st.success(f"✅ **{confidence_threshold:.0f}%** - Medium threshold (Recommended)")
                    else:
                        st.info(f"🔒 **{confidence_threshold:.0f}%** - High threshold (Very strict)")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🔍 Analyze All Images", type="primary", use_container_width=True):
                        use_tta = st.session_state.get('use_tta', True)
                        num_aug = st.session_state.get('num_augmentations', 5)
                        
                        status_text = f"🧠 AI is analyzing {len(uploaded_images)} images with ensemble prediction..."
                        with st.spinner(status_text):
                            progress_bar = st.progress(0)
                            
                            # Predict on each image
                            all_predictions = []
                            all_confidences = []
                            
                            confidence_threshold = st.session_state.get('confidence_threshold', 50.0)
                            
                            for idx, img_file in enumerate(uploaded_images):
                                img = Image.open(img_file).convert('RGB')
                                pred_class, confidence, top3, is_valid = predict_food(
                                    img, model, class_names, 
                                    use_tta=use_tta, 
                                    num_augmentations=num_aug,
                                    confidence_threshold=confidence_threshold
                                )
                                all_predictions.append((pred_class, confidence, top3, is_valid))
                                all_confidences.append(confidence)
                                
                                # Update progress
                                progress_bar.progress((idx + 1) / len(uploaded_images))
                                time.sleep(0.1)
                            
                            progress_bar.empty()
                            
                            # Check how many predictions are valid
                            valid_predictions = [p for p in all_predictions if p[3]]
                            
                            # Ensemble prediction: majority vote with confidence weighting
                            from collections import Counter
                            pred_classes = [p[0] for p in all_predictions]
                            
                            # Weighted voting based on confidence (only valid predictions)
                            class_scores = {}
                            for pred_class, confidence, _, is_valid in all_predictions:
                                if is_valid:  # Only count valid predictions
                                    class_scores[pred_class] = class_scores.get(pred_class, 0) + confidence
                            
                            # Check if we have any valid predictions
                            final_is_valid = len(valid_predictions) >= len(uploaded_images) * 0.5  # At least 50% valid
                            
                            if final_is_valid and class_scores:
                                # Get final prediction
                                final_class = max(class_scores.items(), key=lambda x: x[1])[0]
                                final_confidence = class_scores[final_class] / len(valid_predictions)
                            else:
                                # Not enough valid predictions
                                final_class = "UNKNOWN"
                                final_confidence = sum(all_confidences) / len(all_confidences)
                            
                            # Get consensus top 3
                            all_top3_classes = {}
                            for _, _, top3, _ in all_predictions:
                                for food, conf in top3:
                                    all_top3_classes[food] = all_top3_classes.get(food, 0) + conf
                            
                            final_top3 = sorted(all_top3_classes.items(), key=lambda x: x[1], reverse=True)[:3]
                            final_top3 = [(food, score/len(uploaded_images)) for food, score in final_top3]
                        
                        st.session_state['prediction'] = {
                            'class': final_class,
                            'confidence': final_confidence,
                            'top3': final_top3,
                            'multi_image': True,
                            'num_images': len(uploaded_images),
                            'individual_predictions': all_predictions,
                            'is_valid': final_is_valid
                        }
                        st.rerun()
            
            else:
                # Single image mode
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
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Confidence level selector after image upload
                    st.markdown("### 🎯 Set Confidence Level")
                    confidence_threshold = st.slider(
                        "Choose minimum confidence level for prediction",
                        min_value=30.0,
                        max_value=90.0,
                        value=st.session_state.get('confidence_threshold', 60.0),
                        step=5.0,
                        help="Higher values make the model more strict. Recommended: 60%"
                    )
                    st.session_state['confidence_threshold'] = confidence_threshold
                    
                    # Visual feedback
                    if confidence_threshold < 50:
                        st.warning(f"⚠️ **{confidence_threshold:.0f}%** - Low threshold (More permissive)")
                    elif confidence_threshold <= 70:
                        st.success(f"✅ **{confidence_threshold:.0f}%** - Medium threshold (Recommended)")
                    else:
                        st.info(f"🔒 **{confidence_threshold:.0f}%** - High threshold (Very strict)")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🔍 Analyze Food with AI", type="primary", use_container_width=True):
                        use_tta = st.session_state.get('use_tta', True)
                        num_aug = st.session_state.get('num_augmentations', 5)
                        confidence_threshold = st.session_state.get('confidence_threshold', 50.0)
                        
                        status_text = "🧠 AI is analyzing with Test-Time Augmentation..." if use_tta else "🧠 AI is analyzing..."
                        with st.spinner(status_text):
                            progress_bar = st.progress(0)
                            for i in range(100):
                                time.sleep(0.015 if use_tta else 0.005)
                                progress_bar.progress(i + 1)
                            
                            predicted_class, confidence, top3, is_valid = predict_food(
                                image, model, class_names, 
                                use_tta=use_tta, 
                                num_augmentations=num_aug,
                                confidence_threshold=confidence_threshold
                            )
                            progress_bar.empty()
                    
                        st.session_state['prediction'] = {
                            'class': predicted_class,
                            'confidence': confidence,
                            'top3': top3,
                            'is_valid': is_valid
                        }
                        st.rerun()
        
        with col2:
            st.markdown("### Analysis Results")
            
            if 'prediction' in st.session_state:
                pred = st.session_state['prediction']
                
                # Check if prediction is valid
                if not pred.get('is_valid', True):
                    st.error("⚠️ **Food Not Recognized**")
                    st.markdown("""
                    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                color: white; padding: 20px; border-radius: 10px; margin: 10px 0;'>
                        <h3 style='margin: 0 0 10px 0;'>🚫 Out of Range Detection</h3>
                        <p style='margin: 0;'>The uploaded image appears to be outside our trained food categories. 
                        The AI confidence is only <strong>{:.1f}%</strong>, which is below the threshold.</p>
                    </div>
                    """.format(pred['confidence']), unsafe_allow_html=True)
                    
                    st.info("""
                    **💡 Possible reasons:**
                    - The food is not in our database of 33 Bangladeshi dishes
                    - The image quality is too low or unclear
                    - The food is heavily modified or mixed with other items
                    - The image doesn't contain food
                    
                    **📚 Check our Food Database tab** to see all available categories we can recognize!
                    """)
                    
                    # Still show top 3 as reference
                    with st.expander("📊 Top 3 Possible Matches (Low Confidence)"):
                        st.warning("These predictions have low confidence and may not be accurate:")
                        for i, (food, conf) in enumerate(pred['top3'], 1):
                            emoji = "1️⃣" if i == 1 else "2️⃣" if i == 2 else "3️⃣"
                            st.markdown(f"{emoji} {food.replace('_', ' ').title()}: {conf:.1f}%")
                    
                    st.markdown("---")
                    st.markdown("### 💡 What to do next?")
                    st.markdown("""
                    1. **Check our Food Database** to see if your food is available
                    2. **Try a clearer image** with better lighting
                    3. **Use multiple images** from different angles for better results
                    4. **Make sure the food is clearly visible** in the image
                    """)
                    
                else:
                    # Show multi-image info if applicable
                    if pred.get('multi_image', False):
                        st.markdown(f"""
                        <div style='background: rgba(102, 126, 234, 0.15); padding: 1rem; border-radius: 15px; 
                                    border-left: 4px solid #667eea; margin: 1.5rem 0;'>
                            <h4 style='color: #667eea; margin: 0;'>📸 Multi-Image Analysis</h4>
                            <p style='margin: 0.5rem 0 0 0; color: #d0d0d0;'>
                                Analyzed <strong>{pred['num_images']} images</strong> using ensemble prediction 
                                for <strong>higher accuracy</strong>! 🎯
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Main prediction
                    st.markdown(f"""
                    <div class="prediction-badge">
                        🍽️ {pred['class'].replace('_', ' ').title()}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Confidence
                    st.progress(pred['confidence'] / 100, text=f"Confidence: {pred['confidence']:.1f}%")
                    
                    # Show individual predictions if multi-image
                    if pred.get('multi_image', False):
                        with st.expander(f"📋 Individual Results ({pred['num_images']} images)"):
                            for idx, (pred_class, confidence, _, _) in enumerate(pred.get('individual_predictions', []), 1):
                                agreement = "✅" if pred_class == pred['class'] else "⚠️"
                                st.markdown(f"{agreement} **Image {idx}:** {pred_class.replace('_', ' ').title()} ({confidence:.1f}%)")
                    
                    # Top 3
                    st.markdown("### 🏆 Top 3 Predictions")
                    for i, (food, conf) in enumerate(pred['top3'], 1):
                        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
                        st.markdown(f"{emoji} **{food.replace('_', ' ').title()}**: {conf:.1f}%")
                    
                    # Nutrition
                    nutrition = get_nutrition(pred['class'])
                    
                    st.markdown("---")
                    st.markdown("### 🍴 Food Information")
                    
                    st.markdown(f"**📝 Description:** {nutrition['description']}")
                    st.markdown(f"**🗺️ Origin:** {nutrition['origin']}")
                    st.markdown(f"**⏰ Best Time:** {nutrition['best_time']}")
                    
                    st.markdown("---")
                    st.markdown("### 📊 Nutrition Facts (per 100g)")
                    
                    # Nutrition metrics
                    met_col1, met_col2, met_col3, met_col4 = st.columns(4)
                    met_col1.metric("🔥 Calories", f"{nutrition['calories']} kcal")
                    met_col2.metric("🥩 Protein", f"{nutrition['protein']}g")
                    met_col3.metric("🍚 Carbs", f"{nutrition['carbs']}g")
                    met_col4.metric("🧈 Fat", f"{nutrition['fat']}g")
                    
                    st.markdown(f"**🥗 Fiber:** {nutrition['fiber']}g | **💊 Vitamins:** {nutrition['vitamins']}")
                    st.info(f"**📏 Serving Size:** {nutrition['serving_size']}")
                    
                    st.markdown("---")
                    st.markdown("### 👨‍🍳 How It's Made")
                    st.markdown(f"<div class='info-section'>{nutrition['preparation']}</div>", unsafe_allow_html=True)
                    
                    st.markdown("### 💡 Health Tips")
                    # Handle health_tips as either list or string
                    if isinstance(nutrition.get('health_tips'), list):
                        for tip in nutrition['health_tips']:
                            st.markdown(f"• {tip}")
                    else:
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
                            # Handle health_tips as either list or string
                            if isinstance(food_data.get('health_tips'), list):
                                st.markdown("**Health Tips:**")
                                for tip in food_data['health_tips']:
                                    st.markdown(f"  • {tip}")
                            else:
                                st.markdown(f"**Health Tips:** {food_data['health_tips']}")
    
    # Footer
    st.markdown("---")
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Footer with links and modals
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📖 About", use_container_width=True):
            st.session_state.show_about = True
    
    with col2:
        if st.button("⚙️ How It Works", use_container_width=True):
            st.session_state.show_how_it_works = True
    
    with col3:
        if st.button("🔒 Privacy Policy", use_container_width=True):
            st.session_state.show_privacy = True
    
    with col4:
        st.markdown("""
            <a href="https://github.com/MasudBinMazid/LF-Classifier-App/releases/download/v1.0.0/LF-Classifier-v1.0.0.apk" 
               target="_blank" 
               style="text-decoration: none;">
                <button style="width: 100%; 
                              padding: 0.5rem; 
                              background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                              color: white; 
                              border: none; 
                              border-radius: 0.5rem; 
                              cursor: pointer;
                              font-size: 0.9rem;
                              font-weight: 500;
                              transition: transform 0.2s;">
                    📱 Download Mobile App
                </button>
            </a>
        """, unsafe_allow_html=True)
    
    # Display modals using expanders
    if st.session_state.get('show_about', False):
        with st.expander("📖 About This App", expanded=True):
            st.markdown("""
            **Bangladeshi Food Classifier** is an AI-powered application developed as part of our **Final Year Design Project (FYDP)**.
            
            #### Key Features:
            - 🍽️ **Food Recognition**: Identify Bangladeshi food items from images
            - 📊 **Nutrition Analysis**: Get detailed nutritional information for detected foods
            - 🥗 **Health Insights**: Receive health tips and dietary recommendations
            - 🎯 **High Accuracy**: Powered by deep learning models trained on local cuisine
            
            #### Project Goal:
            This application aims to help users make informed dietary choices by providing instant 
            nutritional information about Bangladeshi food items through advanced computer vision technology.
            """)
            if st.button("Close", key="close_about"):
                st.session_state.show_about = False
                st.rerun()
    
    if st.session_state.get('show_how_it_works', False):
        with st.expander("⚙️ How It Works", expanded=True):
            st.markdown("""
            #### 🔍 Detection Process:
            1. **Upload Image**: Choose a food image from your device
            2. **AI Analysis**: Our deep learning model processes the image
            3. **Food Recognition**: The system identifies the food category
            4. **Nutrition Info**: Detailed nutritional data is displayed
            
            #### 🍛 Supported Categories:
            The app can detect **35 categories of Bangladeshi local food**, including:
            - Traditional dishes (Morog Polao, Bhapa, Shorshe Ilish, etc.)
            - Street food (Fuchka, Singara, Jalebi, etc.)
            - Sweets (Chomchom, Roshmalai, Pera Sondesh, etc.)
            - Common items (Rice, Dal, Chicken, Tea, etc.)
            
            #### 🎯 Features:
            - **Multi-Image Analysis**: Upload multiple images for ensemble prediction
            - **Confidence Levels**: Adjust detection sensitivity (30-90%)
            - **Test-Time Augmentation**: Enhanced accuracy through multiple predictions
            
            ⚠️ **Note**: This app is designed specifically for Bangladeshi local food only.
            """)
            if st.button("Close", key="close_how_it_works"):
                st.session_state.show_how_it_works = False
                st.rerun()
    
    if st.session_state.get('show_privacy', False):
        with st.expander("🔒 Privacy Policy", expanded=True):
            st.markdown("""
            #### 👥 Development Team:
            - **Masud Rana Mamun**
            - **Momen Miah**
            
            #### 📜 Terms of Use:
            - ✅ **Free to Use**: This application is completely free for everyone
            - ✅ **No Copyright Restrictions**: Feel free to use and share
            - 🔒 **Privacy**: Images are processed locally and not stored on servers
            - 📊 **Data Usage**: No personal data is collected or shared
            
            #### 🎓 Academic Project:
            This is a Final Year Design Project (FYDP) created for educational purposes.
            
            #### 📧 Contact:
            For questions or feedback, please reach out through GitHub.
            
            ---
            **© 2025 Bangladeshi Food Classifier | All Rights Reserved**
            """)
            if st.button("Close", key="close_privacy"):
                st.session_state.show_privacy = False
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style='background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); 
                    border-top: 1px solid rgba(255, 255, 255, 0.1); padding: 2rem; 
                    text-align: center; margin-top: 2rem; border-radius: 15px;'>
            <p style='color: #b0b0b0; margin-bottom: 1rem; font-size: 0.9rem;'>
                Bangladeshi Food Classifier &copy; 2025
            </p>
            <p style='margin: 0.5rem 0;'>
                Developed by 
                <a href='https://github.com/MasudBinMazid' target='_blank' 
                   style='color: #667eea; text-decoration: none; font-weight: 600;'>
                    Masud
                </a>
            </p>
            <p style='color: #808080; font-size: 0.85rem; margin-top: 1rem;'>
                Powered by PyTorch • Deep Learning • Computer Vision
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
