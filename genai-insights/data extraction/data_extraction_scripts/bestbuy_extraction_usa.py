import os

INPUT_PATH = 'data/input_files/Moto Edge 2024_BestBuy_United States.txt'
OUTPUT_XLSX = 'data/output_files/' + os.path.basename(INPUT_PATH).rsplit('.', 1)[0] + '.xlsx'

print(OUTPUT_XLSX)

import re, html
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import pandas as pd
from bs4 import BeautifulSoup

IST = ZoneInfo("Asia/Kolkata")

def clean_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()

def mmddyyyy_from_relative(posted_text: str) -> str:
    if not posted_text:
        return ''
    txt = posted_text.strip()
    m = re.search(r"(Posted\s+[^.]+)\.", txt)
    if m:
        txt = m.group(1)
    txt = txt.replace('Posted', '').strip().lower()

    today = datetime.now(tz=IST).date()

    if 'hour' in txt or txt == 'today':
        dt = today
    elif txt.startswith('yesterday'):
        dt = today - timedelta(days=1)
    else:
        md = re.search(r"(\d+)\s+day", txt)
        mw = re.search(r"(\d+)\s+week", txt)
        if md:
            dt = today - timedelta(days=int(md.group(1)))
        elif mw:
            dt = today - timedelta(days=7*int(mw.group(1)))
        else:
            dt = today

    return dt.strftime('%m/%d/%Y')

def parse_bestbuy_reviews(html_text: str, url_override: str = '') -> pd.DataFrame:
    soup = BeautifulSoup(html_text, 'lxml')
    rows = []

    for li in soup.select('li.review-item'):
        author = ''
        a_el = li.select_one('.ugc-author strong') or li.select_one('.ugc-author')
        if a_el:
            author = a_el.get_text(strip=True)

        rating_val = ''
        r_el = li.select_one('.review-rating .visually-hidden') or li.select_one('.review-rating')
        if r_el:
            mm = re.search(r"Rated\s+(\d)", r_el.get_text(' ', strip=True), flags=re.I)
            if mm:
                rating_val = int(mm.group(1))

        title = ''
        t_el = li.select_one('h4.review-title, .review-title')
        if t_el:
            title = t_el.get_text(' ', strip=True)

        date_norm = ''
        d_el = li.select_one('.posted-date-ownership')
        if d_el:
            date_norm = mmddyyyy_from_relative(d_el.get_text(' ', strip=True))

        desc = ''
        b_el = li.select_one('.ugc-review-body-copy, .ugc-review-body, .review-text')
        if b_el:
            for br in b_el.find_all('br'):
                br.replace_with(' ')
            desc = clean_spaces(b_el.get_text(' ', strip=True))

        img_urls = []
        for im in li.select('img'):
            src = (im.get('data-src') or im.get('src') or '').strip()
            if src.startswith('https://'):
                img_urls.append(src)

        image_url = ';'.join(list(dict.fromkeys(img_urls)))

        content = (title + ': ' + desc).strip()

        rows.append({
            'Content': content,
            'Author': author,  # ✅ RENAMED
            'Rating': rating_val,
            'URL': url_override,
            'Image URL': image_url,
            'Date': date_norm,
            'Country': 'United States',
        })

    return pd.DataFrame(rows)

def extract_to_xlsx(input_path: str, output_path: str) -> int:
    import os

    with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
        html_text = f.read()

    df = parse_bestbuy_reviews(html_text)

    # ✅ filename split
    filename = os.path.basename(input_path)
    name_without_ext = os.path.splitext(filename)[0]
    parts = name_without_ext.split('_')

    product = parts[0].strip() if len(parts) > 0 else ''
    source = parts[1].strip().lower() if len(parts) > 1 else ''

    # ✅ add columns
    df['Product'] = product
    df['Source'] = source
    df['isIngested'] = 0

    # ✅ final order
    df = df[
        ['Content','Author','Rating','URL','Image URL','Date','Country','Product','Source','isIngested']
    ]

    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Reviews', index=False)

    return len(df)

count = extract_to_xlsx(INPUT_PATH, OUTPUT_XLSX)
print(f'✅ Extracted {count} reviews → {OUTPUT_XLSX}')