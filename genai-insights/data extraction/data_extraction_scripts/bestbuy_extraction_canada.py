import os

INPUT_PATH = 'data/input_files/Moto Edge 5G 2025_BestBuy_Canada.txt'
OUTPUT_XLSX = 'data/output_files/' + os.path.basename(INPUT_PATH).rsplit('.', 1)[0] + '.xlsx'

print(OUTPUT_XLSX)

from bs4 import BeautifulSoup
import pandas as pd
import re
import os
from datetime import datetime

# ---------- Helpers ----------

def format_date(date_text):
    try:
        dt = datetime.strptime(date_text.strip(), "%B %d, %Y")
        return f"{dt.month}/{dt.day}/{dt.year}"
    except Exception:
        return ""

def extract_country_from_filename(filename):
    if "bestbuy" in filename.lower():
        return "Canada"
    return "Unknown"

# ---------- Parser ----------

def parse_bestbuy_canada(html_text: str, filename: str) -> pd.DataFrame:

    soup = BeautifulSoup(html_text, "html.parser")
    country = extract_country_from_filename(filename)

    reviews_data = []

    review_items = soup.find_all("li", class_="review_1H0vP")

    for review in review_items:

        # Rating
        rating = None
        rating_tag = review.find("p", class_="sr-only")
        if rating_tag:
            match = re.search(r"(\d+)\s+out of\s+5", rating_tag.get_text())
            if match:
                rating = int(match.group(1))

        # Title
        title = ""
        title_tag = review.find("h3", class_="reviewTitle_27zYc")
        if title_tag:
            title = title_tag.get_text(strip=True)

        # Content
        body = ""
        content_div = review.find("div", class_="reviewContent_wpBgx")
        if content_div:
            p = content_div.find("p")
            if p:
                body = p.get_text(strip=True)

        # Final content
        if title and body:
            final_content = f"{title}: {body}"
        elif title:
            final_content = title
        else:
            final_content = body

        # Author (RENAMED)
        author = ""
        author_span = review.select_one(
            "div.reviewerInfo_3YMpL span.author_3-9SJ span span"
        )
        if author_span:
            author = author_span.get_text(strip=True)

        # Date
        formatted_date = ""
        date_span = review.find("span", class_="locationAndTime_FDdpK")
        if date_span:
            raw_date = date_span.get_text(strip=True).replace("-", "").strip()
            formatted_date = format_date(raw_date)

        # Images
        image_urls = []
        image_tags = review.find_all("img", attrs={"data-automation": "review-thumbnail"})
        for img in image_tags:
            src = img.get("src")
            if src:
                image_urls.append(src)

        image_url_str = ";".join(image_urls)

        reviews_data.append({
            "Content": final_content,
            "Author": author,
            "Rating": rating,
            "Image URL": image_url_str,
            "Date": formatted_date,
            "Country": country
        })

    return pd.DataFrame(reviews_data)

# ---------- FINAL FUNCTION ----------

def extract_to_xlsx(input_path: str, output_path: str) -> int:

    with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
        html_text = f.read()

    filename = os.path.basename(input_path)

    df = parse_bestbuy_canada(html_text, filename)

    # filename split
    name_without_ext = os.path.splitext(filename)[0]
    parts = name_without_ext.split('_')

    product = parts[0].strip() if len(parts) > 0 else ''
    source = parts[1].strip().lower() if len(parts) > 1 else ''

    # add columns
    df['Product'] = product
    df['Source'] = source
    df['isIngested'] = 0

    # final column order
    df = df[
        ['Content','Author','Rating','Image URL','Date','Country','Product','Source','isIngested']
    ]

    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Reviews', index=False)

    return len(df)

count = extract_to_xlsx(INPUT_PATH, OUTPUT_XLSX)
print(f'✅ Extracted {count} reviews → {OUTPUT_XLSX}')