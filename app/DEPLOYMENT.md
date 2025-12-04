# 🚀 Deployment Guide - Bangladeshi Food Classifier

## 📦 Pre-Deployment Setup

### 1. Prepare Your Model Files

Before deploying, place these files in the `app/` folder:

```
app/
├── food_classifier_app.py
├── requirements.txt
├── model.pth              ← Your best trained model (rename it)
└── class_names.json       ← Your class names file
```

**Important:** Rename your trained model file (e.g., `best_model_EfficientNet_B3.pth`) to exactly `model.pth`

### 2. Test Locally

```bash
cd app
streamlit run food_classifier_app.py
```

The app should work WITHOUT asking for file uploads.

---

## 🌐 Deploy to Streamlit Cloud (Free)

### Step 1: Push to GitHub

```bash
# Make sure model files are in app folder
cd app
# Commit changes
git add .
git commit -m "Add production model files"
git push origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **"New app"**
4. Select:
   - Repository: `MasudBinMazid/Local-Food-Classifier`
   - Branch: `main`
   - Main file path: `app/food_classifier_app.py`
5. Click **Deploy!**

### Step 3: Wait for Build

- First deployment takes 5-10 minutes
- Streamlit will install all dependencies automatically
- You'll get a public URL like: `https://your-app.streamlit.app`

---

## 🎯 Alternative: Deploy to Hugging Face Spaces

### Step 1: Create Hugging Face Account

Go to [huggingface.co](https://huggingface.co) and create account

### Step 2: Create New Space

1. Click **"New Space"**
2. Name: `bangladeshi-food-classifier`
3. SDK: Select **Streamlit**
4. Visibility: Public (free) or Private

### Step 3: Upload Files

Upload these files to the Space:
- `food_classifier_app.py` (rename to `app.py`)
- `requirements.txt`
- `model.pth`
- `class_names.json`

### Step 4: Done!

Your app will be live at: `https://huggingface.co/spaces/your-username/bangladeshi-food-classifier`

---

## 📝 Important Notes

### Model File Size

- **Streamlit Cloud:** Max 1GB file size (might need to use Git LFS for large models)
- **Hugging Face:** Better for large models (supports Git LFS by default)

### If Model is Too Large (>100MB)

Use **Git LFS** (Large File Storage):

```bash
# Install Git LFS
git lfs install

# Track model file
cd app
git lfs track "*.pth"
git add .gitattributes
git add model.pth
git commit -m "Add model with Git LFS"
git push origin main
```

### Environment Variables (Optional)

For production, you can add authentication or API keys in Streamlit Cloud settings.

---

## 🔒 Security Best Practices

1. ✅ Model files are NOT uploaded by users
2. ✅ No sensitive code exposed
3. ✅ Clean public interface
4. ✅ Fast loading (model cached)

---

## 📊 What Users Will See

- ✅ Clean food classification interface
- ✅ Upload food image button
- ✅ Detailed nutrition information
- ✅ Food database search
- ❌ NO model upload section
- ❌ NO technical details
- ❌ NO settings panel

---

## 🆘 Troubleshooting

### "Model files not found" error

**Solution:** Make sure `model.pth` and `class_names.json` are in the same folder as `food_classifier_app.py`

### Large model won't deploy

**Solution:** Use Git LFS or upload model to Google Drive and download it in app startup

### App is slow

**Solution:** Use a smaller model (EfficientNet-B0 instead of B3) or optimize with model quantization

---

## 📧 Support

For deployment issues, contact the developer or check Streamlit documentation: https://docs.streamlit.io
