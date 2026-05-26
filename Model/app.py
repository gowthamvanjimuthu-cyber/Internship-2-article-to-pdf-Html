from flask import Flask, render_template, request, jsonify, send_file
import os
import uuid
import requests
import trafilatura
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import re
from datetime import datetime

app = Flask(__name__)

DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), 'downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def fetch_article(url):
    """Fetch and extract article content from URL."""
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36'
        )
    }

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')

    # ---------- Metadata ----------
    title = ''
    og_title = soup.find('meta', property='og:title')
    if og_title and og_title.get('content'):
        title = og_title['content']
    if not title:
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)

    author = ''
    for attr in [{'name': 'author'}, {'property': 'article:author'}]:
        tag = soup.find('meta', attr)
        if tag and tag.get('content'):
            author = tag['content']
            break

    description = ''
    for attr in [{'name': 'description'}, {'property': 'og:description'}]:
        tag = soup.find('meta', attr)
        if tag and tag.get('content'):
            description = tag['content']
            break

    # ---------- Content ----------
    content = trafilatura.extract(
        html_content,
        include_comments=False,
        include_tables=True,
        favor_precision=False,
    )

    if not content:
        for selector in ['article', 'main', '.content', '#content', '.post-content', '.entry-content']:
            element = soup.select_one(selector)
            if element:
                content = element.get_text(separator='\n', strip=True)
                break

    if not content:
        content = soup.get_text(separator='\n', strip=True)

    return {
        'title': title or 'Untitled Article',
        'author': author,
        'description': description,
        'content': content or '',
        'url': url,
        'fetched_at': datetime.now().strftime('%B %d, %Y at %I:%M %p'),
    }


def generate_html(article_data):
    """Build a nicely formatted, self-contained HTML document."""
    paragraphs_html = '\n'.join(
        f'        <p>{para.strip()}</p>'
        for para in article_data['content'].split('\n')
        if para.strip()
    )
    author_block = f"By <strong>{article_data['author']}</strong> &nbsp;|&nbsp; " if article_data['author'] else ''
    desc_block = (
        f'    <div class="description">{article_data["description"]}</div>'
        if article_data['description'] else ''
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article_data['title']}</title>
    <style>
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Georgia', 'Times New Roman', serif;
            background: #f5f3ef;
            color: #1a1a1a;
            line-height: 1.85;
        }}
        .header {{
            background: linear-gradient(135deg, #0d1b2a 0%, #1b3a5c 60%, #1a5276 100%);
            color: #fff;
            padding: 64px 40px 48px;
            text-align: center;
        }}
        .badge {{
            display: inline-block;
            background: rgba(255,255,255,0.15);
            border: 1px solid rgba(255,255,255,0.35);
            border-radius: 20px;
            padding: 5px 18px;
            font-size: 11px;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 22px;
        }}
        h1 {{
            font-size: clamp(1.6rem, 4vw, 2.4rem);
            font-weight: 700;
            line-height: 1.3;
            max-width: 820px;
            margin: 0 auto 18px;
        }}
        .meta {{
            font-size: 13px;
            opacity: 0.75;
        }}
        .description {{
            max-width: 820px;
            margin: 32px auto;
            padding: 18px 22px 18px 26px;
            border-left: 4px solid #1a5276;
            background: #fff;
            font-style: italic;
            color: #555;
            font-size: 1.05em;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        }}
        .content-wrap {{
            max-width: 820px;
            margin: 36px auto 60px;
            background: #fff;
            padding: 50px 56px;
            border-radius: 10px;
            box-shadow: 0 4px 28px rgba(0,0,0,0.08);
        }}
        .content-wrap p {{
            margin: 14px 0;
            font-size: 1.05em;
            color: #2c2c2c;
            text-align: justify;
        }}
        .footer {{
            background: #0d1b2a;
            color: rgba(255,255,255,0.55);
            text-align: center;
            padding: 28px 20px;
            font-size: 12px;
        }}
        .footer a {{ color: rgba(255,255,255,0.75); word-break: break-all; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="badge">Article</div>
        <h1>{article_data['title']}</h1>
        <div class="meta">{author_block}Fetched on {article_data['fetched_at']}</div>
    </div>

{desc_block}

    <div class="content-wrap">
{paragraphs_html}
    </div>

    <div class="footer">
        <p>Source: <a href="{article_data['url']}" target="_blank">{article_data['url']}</a></p>
        <p style="margin-top:8px">Converted by Article → PDF / HTML Converter</p>
    </div>
</body>
</html>"""


def generate_pdf(article_data, output_path):
    """Build a clean PDF with ReportLab."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'ATitle',
        parent=styles['Title'],
        fontSize=22,
        fontName='Helvetica-Bold',
        spaceAfter=10,
        textColor=colors.HexColor('#1a5276'),
        alignment=TA_LEFT,
    )
    meta_style = ParagraphStyle(
        'AMeta',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica',
        textColor=colors.HexColor('#777777'),
        spaceAfter=16,
    )
    desc_style = ParagraphStyle(
        'ADesc',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica-Oblique',
        textColor=colors.HexColor('#444444'),
        leftIndent=16,
        rightIndent=16,
        spaceBefore=6,
        spaceAfter=16,
    )
    body_style = ParagraphStyle(
        'ABody',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica',
        leading=18,
        spaceBefore=5,
        spaceAfter=5,
        textColor=colors.HexColor('#2c2c2c'),
        alignment=TA_JUSTIFY,
    )
    url_style = ParagraphStyle(
        'AURL',
        parent=styles['Normal'],
        fontSize=8,
        fontName='Helvetica',
        textColor=colors.HexColor('#999999'),
        alignment=TA_CENTER,
    )

    story = []

    story.append(Paragraph(article_data['title'], title_style))

    meta_parts = []
    if article_data['author']:
        meta_parts.append(f"By {article_data['author']}")
    meta_parts.append(f"Fetched on {article_data['fetched_at']}")
    story.append(Paragraph(' \u00a0|\u00a0 '.join(meta_parts), meta_style))

    story.append(HRFlowable(width='100%', thickness=1.5, color=colors.HexColor('#1a5276')))
    story.append(Spacer(1, 14))

    if article_data['description']:
        safe_desc = (article_data['description']
                     .replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
        story.append(Paragraph(f'\u201c{safe_desc}\u201d', desc_style))
        story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#cccccc')))
        story.append(Spacer(1, 12))

    for para in article_data['content'].split('\n'):
        para = para.strip()
        if not para:
            continue
        safe = para.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        story.append(Paragraph(safe, body_style))

    story.append(Spacer(1, 24))
    story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#cccccc')))
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"Source: {article_data['url']}", url_style))

    doc.build(story)


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    url = (data.get('url') or '').strip()

    if not url:
        return jsonify({'error': 'Please provide a URL.'}), 400
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    try:
        article = fetch_article(url)
    except requests.RequestException as exc:
        return jsonify({'error': f'Failed to fetch article: {exc}'}), 400

    if not article['content']:
        return jsonify({'error': 'Could not extract article content from this URL.'}), 400

    try:
        file_id = str(uuid.uuid4())[:8]
        safe_title = re.sub(r'[^\w\s-]', '', article['title'])[:45].strip().replace(' ', '-')
        base_name = f"{safe_title}_{file_id}" if safe_title else f"article_{file_id}"

        # HTML
        html_path = os.path.join(DOWNLOAD_DIR, f"{base_name}.html")
        with open(html_path, 'w', encoding='utf-8') as fh:
            fh.write(generate_html(article))

        # PDF
        pdf_path = os.path.join(DOWNLOAD_DIR, f"{base_name}.pdf")
        generate_pdf(article, pdf_path)

        return jsonify({
            'success': True,
            'title': article['title'],
            'author': article['author'],
            'html_file': f"{base_name}.html",
            'pdf_file': f"{base_name}.pdf",
        })

    except Exception as exc:
        return jsonify({'error': f'Conversion failed: {exc}'}), 500


@app.route('/download/<filetype>/<filename>')
def download(filetype, filename):
    safe = os.path.basename(filename)
    path = os.path.join(DOWNLOAD_DIR, safe)

    if not os.path.exists(path):
        return jsonify({'error': 'File not found.'}), 404

    mime_map = {'html': 'text/html', 'pdf': 'application/pdf'}
    if filetype not in mime_map:
        return jsonify({'error': 'Invalid file type.'}), 400

    return send_file(path, as_attachment=True, mimetype=mime_map[filetype])


if __name__ == '__main__':
    app.run(debug=True, port=5000)
