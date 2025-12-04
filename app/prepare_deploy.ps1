# Deployment Preparation Script
# Run this before deploying to production

Write-Host "🚀 Preparing for deployment..." -ForegroundColor Cyan
Write-Host ""

# Check if model files exist
$modelPath = "model.pth"
$classPath = "class_names.json"

if (Test-Path $modelPath) {
    Write-Host "✅ Found: model.pth" -ForegroundColor Green
} else {
    Write-Host "❌ Missing: model.pth" -ForegroundColor Red
    Write-Host "   Please copy your best trained model and rename it to 'model.pth'" -ForegroundColor Yellow
}

if (Test-Path $classPath) {
    Write-Host "✅ Found: class_names.json" -ForegroundColor Green
} else {
    Write-Host "❌ Missing: class_names.json" -ForegroundColor Red
    Write-Host "   Please copy your class_names.json file here" -ForegroundColor Yellow
}

Write-Host ""

# Check model size
if (Test-Path $modelPath) {
    $modelSize = (Get-Item $modelPath).Length / 1MB
    Write-Host "📊 Model size: $([math]::Round($modelSize, 2)) MB" -ForegroundColor Cyan
    
    if ($modelSize -gt 100) {
        Write-Host "⚠️  Model is large (>100MB). Consider using Git LFS for deployment." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Test locally: streamlit run food_classifier_app.py"
Write-Host "   2. Commit files: git add . && git commit -m 'Add production files'"
Write-Host "   3. Push to GitHub: git push origin main"
Write-Host "   4. Deploy to Streamlit Cloud or Hugging Face"
Write-Host ""
Write-Host "📖 See DEPLOYMENT.md for detailed instructions" -ForegroundColor Green
