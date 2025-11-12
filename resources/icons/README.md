# Icon Placeholders

This directory contains icon files for the system tray application.

## Required Icons:

1. **icon_idle.png** - Green circle (monitoring active/idle)
2. **icon_downloading.png** - Blue circle with download arrow (downloading)
3. **icon_uploading.png** - Yellow circle with upload arrow (uploading)
4. **icon_error.png** - Red circle with X (error state)
5. **icon_paused.png** - Gray circle (paused state)
6. **app_icon.ico** - Main application icon (for window title and taskbar)

## Icon Specifications:

- **Format**: PNG for tray icons, ICO for application icon
- **Size**: 16x16, 32x32, 48x48 pixels (multiple sizes in ICO)
- **Style**: Flat, modern design with clear visibility
- **Colors**:
  - Green (#4CAF50) - Active/Success
  - Blue (#2196F3) - Downloading
  - Yellow (#FF9800) - Uploading
  - Red (#F44336) - Error
  - Gray (#757575) - Paused

## Creating Icons:

You can create these icons using:
- **Online tools**: favicon.io, icons8.com, flaticon.com
- **Design software**: Adobe Illustrator, Figma, Inkscape
- **Python libraries**: PIL/Pillow (programmatic generation)

### Example with Python (Pillow):

```python
from PIL import Image, ImageDraw

def create_icon(color, filename, size=32):
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, 4, size-4, size-4], fill=color)
    img.save(filename)

# Create icons
create_icon('#4CAF50', 'icon_idle.png')
create_icon('#2196F3', 'icon_downloading.png')
create_icon('#FF9800', 'icon_uploading.png')
create_icon('#F44336', 'icon_error.png')
create_icon('#757575', 'icon_paused.png')
```

## Temporary Solution:

For development/testing, the application will use default system icons if these files are not found.
