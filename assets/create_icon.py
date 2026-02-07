"""
Create a simple tray icon for EasyClaude.
Run with: python assets/create_icon.py
"""

try:
    from PIL import Image, ImageDraw
    import os

    # Create a simple icon with a "C" for Claude
    size = 64
    img = Image.new('RGBA', (size, size), (50, 50, 50, 255))
    draw = ImageDraw.Draw(img)

    # Draw circle
    margin = 4
    draw.ellipse([margin, margin, size - margin, size - margin],
                 fill=(70, 70, 70, 255),
                 outline=(100, 150, 255, 255),
                 width=2)

    # Draw "C"
    draw.text((size // 2, size // 2), "C", fill=(200, 200, 200, 255),
              anchor="mm", font=None)

    # Resize for icon sizes and save as ICO
    icon_sizes = [(16, 16), (32, 32), (48, 48)]
    icon_images = [img.resize(sz, Image.Resampling.LANCZOS) for sz in icon_sizes]

    # Save as ICO
    icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
    icon_images[0].save(icon_path, format='ICO',
                        sizes=[(sz[0], sz[1]) for sz in icon_sizes])

    print(f"Icon created: {icon_path}")

except ImportError:
    print("PIL not available. Install with: pip install Pillow")
    print("Using fallback: will create a simple icon at runtime")
