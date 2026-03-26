from PIL import Image, ImageDraw, ImageFont
import textwrap

def generate_thumbnail(title, subtitle, output_path, 
                       bg_color=(5,5,10), accent_color=(180,0,0),
                       font_path="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
    print("🖼️ Generating thumbnail...")
    img = Image.new("RGB", (1280, 720), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Gradient background
    for y in range(720):
        darkness = int(bg_color[0] + (y/720) * 15)
        draw.line([(0,y),(1280,y)], fill=(darkness, 0, darkness//2))

    # Accent lines
    draw.rectangle([0, 0, 1280, 6], fill=accent_color)
    draw.rectangle([0, 714, 1280, 720], fill=accent_color)

    # Badge
    draw.rectangle([50, 45, 500, 110], fill=accent_color)

    try:
        font_badge = ImageFont.truetype(font_path, 32)
        font_title = ImageFont.truetype(font_path, 55)
        font_sub   = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    except:
        font_badge = ImageFont.load_default()
        font_title = font_badge
        font_sub   = font_badge

    draw.text((60, 55), subtitle, font=font_badge, fill="white")

    lines = textwrap.wrap(title, width=26)
    y_pos = 160
    for line in lines[:3]:
        draw.text((62, y_pos+3), line, font=font_title, fill=(100,0,0))
        draw.text((60, y_pos),   line, font=font_title, fill="white")
        y_pos += 75

    draw.text((60, 650), "FOLLOW FOR MORE 🔴",
              font=font_sub, fill=(255,50,50))

    img.save(output_path, quality=95)
    print("✅ Thumbnail generated!")
