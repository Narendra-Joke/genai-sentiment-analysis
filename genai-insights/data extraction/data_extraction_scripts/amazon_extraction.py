import os

# INPUT_PATH = 'data/input_files/Moto Edge 70 Pro_Flipkart_India.txt'
INPUT_PATH = '../data/input_files/Moto Edge 70 Pro_Flipkart_India.txt'
# OUTPUT_XLSX = '../data/output_files/' + os.path.basename(INPUT_PATH).rsplit('.', 1)[0] + '.xlsx'
OUTPUT_XLSX = '../../data/' + os.path.basename(INPUT_PATH).rsplit('.', 1)[0] + '.xlsx'

print(OUTPUT_XLSX)

import re, html
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import pandas as pd
from bs4 import BeautifulSoup

IST = ZoneInfo('Asia/Kolkata')

# --- Domain mapping helpers ---
def map_country_to_domain(country: str) -> str:
    if not country:
        return "amazon.com"
    c = country.strip().lower()
    country_to_domain = {
        "india": "amazon.in",
        "united states": "amazon.com",
        "united kingdom": "amazon.co.uk",
        "germany": "amazon.de",
        "canada": "amazon.ca",
    }
    return country_to_domain.get(c, "amazon.com")

def make_review_url(review_id: str, country: str) -> str:
    domain = map_country_to_domain(country)
    return f"https://{domain}/gp/customer-reviews/{review_id}"

# --- Utilities ---
def normalize_date(raw: str) -> str:
    if not raw:
        return ''
    txt = raw.strip()
    today = datetime.now(tz=IST)

    if txt.lower() == 'today':
        return today.strftime('%m/%d/%Y')
    if txt.lower() == 'yesterday':
        return (today - timedelta(days=1)).strftime('%m/%d/%Y')

    try:
        dt = datetime.strptime(txt, '%B %d, %Y').replace(tzinfo=IST)
        return dt.strftime('%m/%d/%Y')
    except:
        pass

    try:
        dt = datetime.strptime(txt, '%d %B %Y').replace(tzinfo=IST)
        return dt.strftime('%m/%d/%Y')
    except:
        pass

    return ''

def extract_country_and_date(text: str):
    m = re.search(r'in\s+([A-Za-z ]+)\s+on\s+(.+)', text)
    if m:
        return m.group(1).strip(), normalize_date(m.group(2))
    return '', normalize_date(text)

def clean_text(s: str) -> str:
    if not s:
        return ''
    s = re.sub(r'<[^>]*>', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    return html.unescape(s).strip()

# --- Parser (UNCHANGED LOGIC) ---
def parse_amazon_reviews(html_text: str) -> pd.DataFrame:
    soup = BeautifulSoup(html_text, 'html.parser')
    rows = []

    for li in soup.select('li.review[data-hook="review"]'):
        author = ''
        a_name = li.select_one('.a-profile-name')
        if a_name:
            author = a_name.get_text(strip=True)

        title_text, rating_val, review_id = '', '', None

        a_title = li.select_one('[data-hook="review-title"]')
        if a_title:
            t_text = a_title.get_text(" ", strip=True)
            m = re.match(r'([\d.]+)\s+out of 5 stars\s+(.*)', t_text)
            if m:
                rating_val = int(float(m.group(1)))
                title_text = m.group(2)
            else:
                title_text = t_text

            href = a_title.get('href','')
            m2 = re.search(r'/gp/customer-reviews/([A-Za-z0-9]+)', href)
            if m2:
                review_id = m2.group(1)

        country, date_val = '', ''
        date_span = li.select_one('[data-hook="review-date"]')
        if date_span:
            country, date_val = extract_country_and_date(date_span.get_text(strip=True))

        url = make_review_url(review_id, country) if review_id else ''

        desc = ''
        desc_span = li.select_one('[data-hook="review-body"]')
        if desc_span:
            desc = clean_text(desc_span.get_text(" ", strip=True))

        images = [img.get('src') for img in li.select('img') if img.get('src','').startswith('https://')]
        image_url = ', '.join(images)

        content = f"{title_text} : {desc}".strip()

        rows.append({
            'Content': content,
            'Author Name': author,
            'Rating': rating_val,
            'URL': url,
            'Image URL': image_url,
            'Date': date_val,
            'Country': country
        })

    return pd.DataFrame(rows)

# --- FINAL FUNCTION (ONLY ADDITION PART) ---
def extract_to_xlsx(input_path: str, output_path: str) -> int:
    import os

    with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
        html_text = f.read()

    df = parse_amazon_reviews(html_text)

    # ✅ Extract Product & Source from filename
    filename = os.path.basename(input_path)
    name_without_ext = os.path.splitext(filename)[0]
    parts = name_without_ext.split('_')

    product = parts[0].strip() if len(parts) > 0 else ''
    source = parts[1].strip().lower() if len(parts) > 1 else ''

    # ✅ Add new columns
    df['Product'] = product
    df['Source'] = source
    df['isIngested'] = 0

    # ✅ Column order
    df = df[
        ['Content','Author Name','Rating','URL','Image URL','Date','Country','Product','Source','isIngested']
    ]

    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Reviews', index=False)

    return len(df)

count = extract_to_xlsx(INPUT_PATH, OUTPUT_XLSX)
print(f'✅ Extracted {count} reviews → {OUTPUT_XLSX}')
