
import requests
import os
import pandas as pd
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

def reduce_name(name):
    CUTOFF = 20
    if len(name) > CUTOFF and len(name) <= CUTOFF+4 and name[:4] == "The ": 
        return name[4:]
    elif len(name) > CUTOFF:
        words = name.split()
        return ' '.join(words[:3]) + "..."
    else:
        return name

def reduce_author_name(name):
    CUTOFF = 25
    if len(name) > CUTOFF:
        words = name.split()
        if len(words) > 2: 
            return ' '.join([words[0], words[-1]])
        else:
            return words[-1] 
    else:
        return name
    
df = pd.read_csv('details.csv')
df.columns = ["rank", "name", "author", "image"]
df["rank"] = df["rank"].apply(lambda x: x + 1)
df.name = df.name.apply(lambda x: reduce_name(x))
df.author = df.author.apply(lambda x: reduce_author_name(x))
    
def create_book_grid(df, output_path, grid_width=10, cover_size=(100, 150), margin=(40, 50), DARK_MODE=False):
    col = "#000"
    back = "#FCF5E5"
    if DARK_MODE: 
        col = "#FFF"
        back = "#2c2005"

    num_books = len(df)
    num_rows = (num_books + grid_width - 1) // grid_width  # Ceiling division
    
    cover_width, cover_height = cover_size
    margin_x, margin_y = margin
    final_width = grid_width * (cover_width + margin_x) + margin_x + 10
    final_height = num_rows * (cover_height + margin_y) + margin_y + margin_y + 20

    # Create a new image with parchment brown background
    final_image = Image.new('RGB', (final_width, final_height), back)
    draw = ImageDraw.Draw(final_image)

    # Load a font for ranking, title, and author text
    try:
        font = ImageFont.truetype("EBGaramond-Regular.ttf", 12)
        author_font = ImageFont.truetype("EBGaramond-Italic.ttf", 11)
    except IOError:
        print("Failed to load font.")
        font = ImageFont.load_default()
        author_font = ImageFont.load_default()
        
    try:
        title_font = ImageFont.truetype("EBGaramond-Regular.ttf", 36)
        subtitle_font = ImageFont.truetype("EBGaramond-Regular.ttf", 24)
    except IOError:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        
    title_text = "The Greatest Books of all Time"
    subtitle_text = "Generated from thegreatestbooks.org, compiled from 300+ lists of books."

    # Calculate position for title and subtitle
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
    title_width = title_bbox[2] - title_bbox[0]
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    title_x = (final_width - title_width) // 2
    subtitle_x = (final_width - subtitle_width) // 2
    title_y = 20
    subtitle_y = title_y + title_font.getmetrics()[0] + 10

    # Draw title and subtitle on the image
    draw.text((title_x, title_y), title_text, fill=col, font=title_font)
    draw.text((subtitle_x, subtitle_y), subtitle_text, fill=col, font=subtitle_font)
    
    start_y = title_y + margin_y

    for index, row in df.iterrows():
        # Get book details
        rank = row['rank']
        title = row['name']
        author = row['author']
        cover_path = "images/" + row['image']

        # Open and resize the cover image
        if os.path.exists(cover_path):
            cover_image = Image.open(cover_path).resize(cover_size)
        else:
            print(f"Cover image not found: {cover_path}")
            continue

        # Calculate position in the grid
        row_num = index // grid_width
        col_num = index % grid_width
        x = col_num * (cover_width + margin_x) + margin_x
        y = start_y + row_num * (cover_height + margin_y) + margin_y

        # Paste the cover image onto the final image
        final_image.paste(cover_image, (x, y))

        # Draw the rank, title, and author below the cover image
        text_y_offset = cover_height + 5
        draw.text((x, y + text_y_offset), f"{rank}. {title}", fill=col, font=font)
        draw.text((x, y + text_y_offset + 15), f"{author}", fill=col, font=author_font)

    final_image.save(output_path)

create_book_grid(df, 'top_100_books.png')
create_book_grid(df, 'top_100_books_dark.png', DARK_MODE=True)
