"""
Script to generate a high-res, professional Legion FPS icon and save as .ico and .png.
"""

import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_legion_fps_icon(output_ico_path: str, output_png_path: str):
    size = 512
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Outer Dark Squircle Container
    padding = 24
    squircle_box = [padding, padding, size - padding, size - padding]
    corner_radius = 110

    # Draw dark rounded background
    draw.rounded_rectangle(
        squircle_box,
        radius=corner_radius,
        fill="#0e131d",
        outline="#242c3d",
        width=6
    )

    # 2. Subtle radial glow layer
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    cx, cy = size // 2, size // 2

    for r in range(160, 60, -10):
        alpha = int(18 * (1.0 - (r - 60) / 100))
        glow_draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(0, 210, 255, alpha))

    glow = glow.filter(ImageFilter.GaussianBlur(16))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)

    # 3. Outer Circular Gauge Track
    gauge_padding = 64
    g_box = [gauge_padding, gauge_padding, size - gauge_padding, size - gauge_padding]
    stroke_w = 26
    draw.ellipse(g_box, outline="#1c2536", width=stroke_w)

    # 4. Glowing Neon Arc (Starts at -110 deg, sweeps 270 deg)
    # Draw vibrant cyan / mint gradient arc
    draw.arc(g_box, start=-120, end=135, fill="#00d2ff", width=stroke_w)
    
    # Cap dot at the head of the arc
    end_angle_rad = math.radians(135)
    gr = (size - 2 * gauge_padding) / 2
    dot_x = cx + gr * math.cos(end_angle_rad)
    dot_y = cy + gr * math.sin(end_angle_rad)
    dot_r = stroke_w // 2
    draw.ellipse([dot_x - dot_r, dot_y - dot_r, dot_x + dot_r, dot_y + dot_r], fill="#38f8d4")

    # 5. Legion Emblem / Gaming Y-Shape in Center
    # We draw the iconic Legion 3-pointed star / stylized geometry
    # Center core point (cx, cy - 10)
    top_y = cy - 85
    left_x = cx - 75
    right_x = cx + 75
    bot_y = cy + 45

    # Top branch
    draw.polygon([(cx - 16, top_y + 35), (cx + 16, top_y + 35), (cx + 20, top_y), (cx, top_y - 20), (cx - 20, top_y)], fill="#00e5ff")
    
    # Bottom Left branch
    draw.polygon([(cx - 15, cy + 5), (cx - 35, cy + 20), (left_x, bot_y), (left_x + 15, bot_y + 15), (cx - 5, cy + 25)], fill="#38bdf8")

    # Bottom Right branch
    draw.polygon([(cx + 15, cy + 5), (cx + 35, cy + 20), (right_x, bot_y), (right_x - 15, bot_y + 15), (cx + 5, cy + 25)], fill="#38bdf8")

    # Center triangle hub
    draw.polygon([(cx, cy - 25), (cx - 22, cy + 12), (cx + 22, cy + 12)], fill="#ffffff")

    # 6. "FPS" Badge at bottom inside squircle
    badge_w = 120
    badge_h = 36
    badge_y = cy + 105
    draw.rounded_rectangle(
        [cx - badge_w // 2, badge_y, cx + badge_w // 2, badge_y + badge_h],
        radius=12,
        fill="#00d2ff"
    )

    # Text "FPS"
    try:
        font = ImageFont.truetype("segoeuib.ttf", 22)
    except Exception:
        font = ImageFont.load_default()

    draw.text((cx, badge_y + badge_h // 2 - 1), "FPS", fill="#0a0e17", font=font, anchor="mm")

    # Save PNG
    img.save(output_png_path, format="PNG")

    # Save Multi-resolution ICO (256, 128, 64, 48, 32, 16)
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    img.save(output_ico_path, format="ICO", sizes=sizes)
    print(f"Icon successfully generated at:\nPNG: {output_png_path}\nICO: {output_ico_path}")

if __name__ == "__main__":
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(base_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    ico = os.path.join(assets_dir, "icon.ico")
    png = os.path.join(assets_dir, "icon.png")
    create_legion_fps_icon(ico, png)
