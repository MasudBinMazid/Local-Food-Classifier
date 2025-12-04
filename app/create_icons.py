"""
Quick Icon Generator for PWA
Creates app icons from a base image
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_emoji_icon():
    """Create a simple icon with food emoji"""
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    for size in sizes:
        # Create a gradient background
        img = Image.new('RGB', (size, size), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw gradient background
        for i in range(size):
            r = int(102 + (118 - 102) * i / size)
            g = int(126 + (75 - 126) * i / size)
            b = int(234 + (162 - 234) * i / size)
            draw.rectangle([(0, i), (size, i+1)], fill=(r, g, b))
        
        # Add text emoji (works on most systems)
        try:
            # Try to load a font that supports emoji
            font_size = int(size * 0.6)
            font = ImageFont.truetype("seguiemj.ttf", font_size)  # Windows emoji font
        except:
            try:
                font = ImageFont.truetype("Apple Color Emoji.ttc", font_size)  # Mac
            except:
                font = None
        
        # Draw emoji in center
        text = "🍛"
        if font:
            # Get text size
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Center the text
            x = (size - text_width) // 2
            y = (size - text_height) // 2 - bbox[1]
            
            draw.text((x, y), text, font=font, embedded_color=True)
        else:
            # Fallback: draw a simple food icon
            # Draw a bowl shape
            padding = size // 5
            draw.ellipse(
                [padding, padding, size-padding, size-padding],
                fill='white',
                outline='#667eea',
                width=max(2, size//50)
            )
            # Draw rice/food in bowl
            for i in range(3):
                for j in range(3):
                    x = padding + (size - 2*padding) * (i+1) // 4
                    y = padding + (size - 2*padding) * (j+1) // 4
                    r = size // 20
                    draw.ellipse([x-r, y-r, x+r, y+r], fill='#FFA500')
        
        # Save icon
        filename = f"icon-{size}.png"
        img.save(filename)
        print(f"✅ Created {filename}")
    
    print("\n🎉 All icons created successfully!")
    print("Icons are saved in the current directory.")

def create_from_image(image_path):
    """Create icons from an existing image"""
    try:
        base_image = Image.open(image_path)
        sizes = [72, 96, 128, 144, 152, 192, 384, 512]
        
        for size in sizes:
            icon = base_image.resize((size, size), Image.Resampling.LANCZOS)
            filename = f"icon-{size}.png"
            icon.save(filename)
            print(f"✅ Created {filename}")
        
        print("\n🎉 All icons created successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please make sure the image file exists and is a valid format.")

if __name__ == "__main__":
    print("🎨 PWA Icon Generator\n")
    print("Choose an option:")
    print("1. Create gradient icons with emoji/food symbol")
    print("2. Create icons from your own image")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        print("\n📱 Creating gradient icons with food symbol...")
        create_emoji_icon()
    elif choice == "2":
        image_path = input("Enter path to your image (e.g., food.png): ").strip()
        print(f"\n📱 Creating icons from {image_path}...")
        create_from_image(image_path)
    else:
        print("❌ Invalid choice. Please run the script again.")
    
    print("\n📋 Next steps:")
    print("1. Move all icon-*.png files to your app/ folder")
    print("2. Commit and push to GitHub")
    print("3. Deploy your app!")
