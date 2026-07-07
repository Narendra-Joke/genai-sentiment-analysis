import os

# Parameters: set your input and output paths
INPUT_PATH = 'data/input_files/Moto Edge 70 Fusion_Flipkart.txt'  # change this to your uploaded txt file
OUTPUT_XLSX = 'data/output_files/' + os.path.basename(INPUT_PATH).rsplit('.', 1)[0] + '.xlsx'  # same name with .xlsx extension
print(OUTPUT_XLSX)

import os
import re, html
from datetime import datetime, timedelta, timezone
from typing import List, Dict
import pandas as pd

IST = timezone(timedelta(hours=5, minutes=30))

def now_ist() -> datetime:
    return datetime.now(tz=IST)

def html_unescape(s: str) -> str:
    return html.unescape(s) if s else s

def strip_tags(s: str) -> str:
    if not s:
        return s
    s = re.sub(r'<br\s*/?>', ' ', s, flags=re.IGNORECASE)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = html_unescape(s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def normalize_description(raw: str) -> str:
    if not raw:
        return ''
    raw = re.sub(r'\bREAD\s*MORE\b', '', raw, flags=re.IGNORECASE)
    raw = strip_tags(raw)
    raw = re.sub(r'\s+([,.!?;:])', r'\1', raw)
    return raw.strip()

def parse_relative_date(rel: str) -> str:
    if not rel:
        return ''
    rel_clean = rel.strip().lower()
    base = now_ist().date()
    if 'today' in rel_clean:
        d = base
    elif 'yesterday' in rel_clean:
        d = base - timedelta(days=1)
    else:
        m = re.search(r'(\d+)\s+days?\s+ago', rel_clean)
        if m:
            d = base - timedelta(days=int(m.group(1)))
        else:
            d = base
    return d.strftime('%m/%d/%Y')

def combine_content(title: str, description: str) -> str:
    title = (title or '').strip()
    description = (description or '').strip()
    return f'{title}: {description}'.strip(': ').strip() if title and description else (title or description)

def dedupe_preserve_order(items: List[str]) -> List[str]:
    seen, out = set(), []
    for x in items:
        if x not in seen:
            out.append(x); seen.add(x)
    return out

def parse_class_based(full_text: str) -> List[Dict[str, str]]:
    reviews = []
    row_splits = re.split(r'<div\s+class="lvJbLV\s+col-12-12"[^>]*>', full_text, flags=re.IGNORECASE)
    if len(row_splits) <= 1:
        return reviews
    for raw_block in row_splits[1:]:
        block = raw_block
        title = ''
        m_title = re.search(r'<p\s+class="qW2QI1"[^>]*>(.*?)</p>', block, flags=re.IGNORECASE|re.DOTALL)
        if m_title:
            title = strip_tags(m_title.group(1))
        description = ''
        m_desc = re.search(r'<div\s+class="G4PxIA"[^>]*>\s*<div[^>]*>\s*<div[^>]*>([\s\S]*?)</div>', block, flags=re.IGNORECASE)
        if m_desc:
            description = normalize_description(m_desc.group(1))
        rating = ''
        m_rating = re.search(r'<div\s+class="MKiFS6\s+ojKpP6"[^>]*>(\d(?:\.\d)?)', block, flags=re.IGNORECASE)
        if m_rating:
            rating = re.sub(r'\.0$', '', m_rating.group(1))
        author = ''
        m_author = re.search(r'<p\s+class="zJ1ZGa\s+ZDi3w2"[^>]*>(.*?)</p>', block, flags=re.IGNORECASE|re.DOTALL)
        if m_author:
            author = strip_tags(m_author.group(1))
        date_str = ''
        candidates = re.findall(r'<p\s+class="zJ1ZGa"[^>]*>(.*?)</p>', block, flags=re.IGNORECASE|re.DOTALL)
        rel_val = ''
        for cand in candidates:
            txt = strip_tags(cand)
            if re.fullmatch(r'(?:Today|Yesterday|\d+\s+days?\s+ago)', txt, flags=re.IGNORECASE):
                rel_val = txt; break
        if rel_val:
            date_str = parse_relative_date(rel_val)
        image_urls = []
        search_area = block
        img_section_match = re.search(r'<div\s+class="HVjhhI\s+m8Qt9R"[^>]*>([\s\S]*?)</div>\s*</div>', block, flags=re.IGNORECASE)
        if img_section_match:
            search_area = img_section_match.group(1)
        for s in re.findall(r'style="[^"]*background-image:\s*url\(([^)]+)\)[^"]*"', search_area, flags=re.IGNORECASE):
            for u in re.findall(r'https?://[^\s\)"]+\.jpg', s, flags=re.IGNORECASE):
                image_urls.append(html_unescape(u))
        image_urls = dedupe_preserve_order(image_urls)
        url = ''
        m_url = re.search(r'<a[^>]+href="(/reviews/[^"]*reviewId=[a-f0-9-]+[^"]*)"', block, flags=re.IGNORECASE)
        if m_url:
            url = 'https://www.flipkart.com' + html_unescape(m_url.group(1))
        content = combine_content(title, description)
        if content:
            reviews.append({
                'Content': content,
                'Author': author,
                'Rating': rating,
                'URL': url,
                'Image URL': ', '.join(image_urls),
                'Date': date_str,
                'Country': 'India'
            })
    return reviews

def parse_fallback(full_text: str) -> List[Dict[str, str]]:
    text = full_text
    pid = ''
    m_pid = re.search(r'pid=([A-Z0-9]{12,})', text)
    if m_pid:
        pid = m_pid.group(1)
    anchors = [m.start() for m in re.finditer(r'Review for:', text)]
    if not anchors:
        return []
    anchors.append(len(text))
    reviews = []
    for i in range(len(anchors) - 1):
        anchor = anchors[i]
        next_anchor = anchors[i+1]
        block_start = max(0, anchor - 2000)
        block_end = next_anchor
        block = text[block_start:block_end]
        rel_anchor = anchor - block_start
        title, rating = '', ''
        bidx = block.rfind('>•<', 0, rel_anchor)
        if bidx != -1:
            prev_slice = block[max(0, bidx-600):bidx]
            m_rat = re.search(r'>([1-5]\.0)<', prev_slice)
            if m_rat:
                rating = re.sub(r'\.0$', '', m_rat.group(1))
            candidates = re.findall(r'>\s*([^<>]{1,200}?)\s*<', block[bidx:rel_anchor])
            if candidates:
                title = candidates[-1].strip()
        desc = ''
        post = block[rel_anchor:]
        m_desc = re.search(r'Review for:[\s\S]*?</div><div[^>]*><span[^>]*>([\s\S]*?)</span>', post, flags=re.IGNORECASE)
        if m_desc:
            desc = normalize_description(m_desc.group(1))
        author = ''
        after_desc_start = rel_anchor + (m_desc.end() if m_desc else 0)
        author_search_area = block[after_desc_start:]
        m_author = re.search(r'>\s*([^<>]{2,100}?)\s*</div>\s*<div[^>]*>\s*,', author_search_area)
        if m_author:
            author = m_author.group(1).strip()
        date_str = ''
        ds = block[after_desc_start:]
        m_rel = re.search(r'Verified Purchase[\s\S]*?·\s*(Today|Yesterday|\d+\s+days? ago)', ds, flags=re.IGNORECASE)
        if m_rel:
            date_str = parse_relative_date(m_rel.group(1))
        img_urls = re.findall(r'https?://[^\s\)"]+flixcart[^\s\)"]+\.jpg', block, flags=re.IGNORECASE)
        img_urls = dedupe_preserve_order([html_unescape(u) for u in img_urls])
        url = ''
        m_url = re.search(r'(/reviews/[^\s"\']*reviewId=[a-f0-9-]+)', block, flags=re.IGNORECASE)
        if m_url:
            url = 'https://www.flipkart.com' + m_url.group(1)
        elif pid:
            obs = re.search(r'data-observerid-[a-f0-9-]+="([a-f0-9-]+)"', block[rel_anchor:], flags=re.IGNORECASE)
            if obs:
                guid = obs.group(1)
                url = f'https://www.flipkart.com/reviews/{pid}?reviewId={guid}'
        content = combine_content(title, desc)
        if content:
            reviews.append({
                'Content': content,
                'Author': author,
                'Rating': rating,
                'URL': url,
                'Image URL': ', '.join(img_urls),
                'Date': date_str,
                'Country': 'India'
            })
    return reviews

def extract_to_xlsx(input_path: str, output_path: str) -> int:
    import os  # local import so no change above

    with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
        full_text = f.read()

    rows = parse_class_based(full_text)
    if not rows:
        rows = parse_fallback(full_text)

    # ✅ extract from filename (NO IMPACT TO PARSING)
    filename = os.path.basename(input_path)
    name_without_ext = os.path.splitext(filename)[0]
    parts = name_without_ext.split('_')

    product = parts[0].strip() if len(parts) > 0 else ''
    source = parts[1].strip().lower() if len(parts) > 1 else ''

    for r in rows:
        r['Content'] = (r.get('Content') or '').strip().strip(':').strip()
        r['Author'] = (r.get('Author') or '').strip()
        r['Rating'] = (r.get('Rating') or '').strip()
        r['URL'] = (r.get('URL') or '').strip()
        r['Image URL'] = (r.get('Image URL') or '').strip()
        r['Date'] = (r.get('Date') or '').strip()
        r['Country'] = 'India'

        # ✅ ONLY ADD THESE 3 LINES
        r['Product'] = product
        r['Source'] = source
        r['isIngested'] = 0

    # ✅ just extend columns (order optional)
    df = pd.DataFrame(rows, columns=[
        'Content',
        'Author',
        'Rating',
        'URL',
        'Image URL',
        'Date',
        'Country',
        'Product',
        'Source',
        'isIngested'
    ])

    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Reviews', index=False)

    return len(df)

# Run extraction
count = extract_to_xlsx(INPUT_PATH, OUTPUT_XLSX)
print(f'✅ Extracted {count} reviews → {OUTPUT_XLSX}')
