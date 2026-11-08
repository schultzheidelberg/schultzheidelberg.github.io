#!/usr/bin/env python3
"""Create the four-page A4 portfolio handout from approved public content.

Run python3 export_portfolio.py, then python3 build.py to publish the download.
Requires ReportLab, Pillow and the same system fonts used by our bibliography.
No network access or private source material is used. All QR codes point to the
stable public homepage, and all diagrams retain their original proportions.
"""
from io import BytesIO
import json
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / 'data' / 'Michael_Schultz_Portfolio.pdf'
ASSETS = ROOT / 'assets'
URL = 'https://schultzheidelberg.github.io/'
EMAIL = 'schultz.consulting@outlook.com'
EDITION = 'November 2026'
W, H = A4
M = 45
CW = W - 2 * M
INK = colors.HexColor('#1a2b34')
GREEN = colors.HexColor('#356b54')
MUTED = colors.HexColor('#53635e')
LINE = colors.HexColor('#d6ded8')

for name, path in [
    ('Body', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
    ('BodyBold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
    ('Display', '/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf'),
    ('DisplayItalic', '/usr/share/fonts/truetype/liberation2/LiberationSerif-Italic.ttf'),
]:
    pdfmetrics.registerFont(TTFont(name, path))
pdfmetrics.registerFontFamily('Body', normal='Body', bold='BodyBold', italic='Body', boldItalic='BodyBold')

c = canvas.Canvas(str(OUTPUT), pagesize=A4, pageCompression=1)
c.setTitle('Michael Schultz | Research & Project Portfolio')
c.setAuthor('Michael Schultz')
c.setSubject('Earth observation, open geospatial data, climate and environmental decision support')
c.setKeywords('Michael Schultz, portfolio, remote sensing, FRAME, PAABS, World Bank, WWF, REDD+')
c.setCreator('Michael Schultz portfolio exporter')
c.setViewerPreference('PrintScaling', 'None')


def paragraph(text, x, top, width, size=10.2, leading=14.6, font='Body', color=INK, max_bottom=H-20):
    style = ParagraphStyle('block', fontName=font, fontSize=size, leading=leading,
                           textColor=color, spaceAfter=0, allowWidows=0, allowOrphans=0)
    p = Paragraph(text, style)
    _, height = p.wrap(width, 1000)
    if top + height > max_bottom:
        raise ValueError(f'Text outside its layout: {top + height:.1f} > {max_bottom}: {text[:70]}')
    p.drawOn(c, x, H - top - height)
    return top + height


def label(text, x, top, width=CW):
    return paragraph(escape(text.upper()), x, top, width, 7.8, 11, 'BodyBold', GREEN)


def rule(top, x=M, width=CW):
    c.setStrokeColor(LINE)
    c.setLineWidth(.55)
    c.line(x, H - top, x + width, H - top)


def linked(label_text, url, x, top, width, size=9.1, leading=13):
    return paragraph(f'<link href="{escape(url)}" color="#356b54">{escape(label_text)}</link>',
                     x, top, width, size, leading)


def picture(filename, x, top, width, height, link=None):
    """Contain the complete source image; retain the white paper around it."""
    im = Image.open(ASSETS / filename).convert('RGB')
    iw, ih = im.size
    scale = min(width / iw, height / ih)
    dw, dh = iw * scale, ih * scale
    dx, dy = x + (width - dw) / 2, H - top - (height + dh) / 2
    # JPEG is used only as an in-memory PDF image encoding for compact handouts.
    buf = BytesIO()
    im.save(buf, format='JPEG', quality=94, subsampling=0)
    buf.seek(0)
    c.drawImage(ImageReader(buf), dx, dy, dw, dh)
    if link:
        c.linkURL(link, (dx, dy, dx + dw, dy + dh), relative=0, thickness=0)
    return top + height


def qr_code(top=32, size=82):
    x = W - M - size
    code = qr.QrCodeWidget(URL, barLevel='M', barBorder=4, barFillColor=colors.black)
    x0, y0, x1, y1 = code.getBounds()
    drawing = Drawing(size, size, transform=[size / (x1-x0), 0, 0, size / (y1-y0), 0, 0])
    drawing.add(code)
    renderPDF.draw(drawing, c, x, H - top - size)
    c.linkURL(URL, (x, H-top-size, x+size, H-top), relative=0, thickness=0)
    paragraph('SCAN FOR MY WEBSITE', x-4, top+size+2, size+8, 6.4, 8, 'BodyBold', GREEN)


def page_header(section, title, subtitle=None):
    qr_code(size=76)
    label(f'Michael Schultz  /  {section}', M, 40, CW-100)
    end = paragraph(title, M, 62, CW-105, 26, 29, 'Display')
    if subtitle:
        paragraph(subtitle, M, end+4, CW-100, 9.5, 13.5, color=MUTED)
    rule(147)


def page_footer(number, note):
    rule(790)
    linked('schultzheidelberg.github.io', URL, M, 800, 230, 8.0, 10)
    paragraph(f'{EDITION}  ·  {number} / 4', W-M-125, 800, 125, 7.8, 10, color=MUTED)
    if note:
        paragraph(note, M, 768, CW, 6.8, 9, color=MUTED, max_bottom=788)
    c.showPage()


def project(top, number, title, context, body, image, links, height=215, caption=None,
            body_size=10.0, image_height=143, image_link=None):
    bottom = top + height
    iw, gap = 211, 22
    tx, tw = M + iw + gap, CW - iw - gap
    label(number, M, top, iw)
    picture(image, M, top+20, iw, image_height, image_link)
    if caption:
        paragraph(caption, M, top+image_height+27, iw, 7.2, 10, color=MUTED, max_bottom=bottom)
    y = paragraph(title, tx, top, tw, 17.8, 20.5, 'Display', max_bottom=bottom)
    y = paragraph(context, tx, y+7, tw, 8.1, 11.4, color=GREEN, max_bottom=bottom)
    y = paragraph(body, tx, y+10, tw, body_size, body_size*1.43, max_bottom=bottom)
    for text, url in links:
        y = linked(text, url, tx, y+7, tw, 8.8, 12.5)
    if y > bottom:
        raise ValueError(f'Project {number} overflows by {y-bottom:.1f} pt')
    return bottom


# 1 — Profile, flood risk and trade.
qr_code(top=36, size=87)
label('Research & project portfolio', M, 42, CW-110)
paragraph('Dr. Michael Schultz', M, 62, CW-108, 29, 33, 'Display')
paragraph('Acting Professor of Remote Sensing', M, 108, CW-105, 10.7, 15, 'BodyBold')
paragraph('Friedrich Schiller University Jena', M, 125, CW-105, 10.3, 14.4)
paragraph('University of Tübingen · Based in Tübingen, Germany', M, 144, CW, 9.1, 13, color=MUTED)
picture('michael-schultz.webp', M, 176, 69, 69)
paragraph('From space to better decisions.', M+87, 173, CW-87, 18.5, 22, 'Display')
paragraph('I connect satellite observations, machine learning and open data with questions about '
          'land use, climate, infrastructure and environmental change. My work combines research '
          'methods with practical platforms for exploration, reporting and decision-making.',
          M+87, 204, CW-87, 10.2, 14.8)
label('Current work  /  Flood risk & trade', M, 284)
rule(302)
project(321, '01 · Huế / Central Vietnam',
        'Flood Risk Adaptation Measures and Evaluation',
        'FRAME · FloodAdaptVN · BMFTR funding',
        'Flood scenarios, exposure and adaptation options for Huế and Central Vietnam. '
        'I connect geospatial research with accessible tools for exploring flood risk and local planning.',
        'frame-home.webp', [('framefavn.org', 'https://framefavn.org/')], height=206,
        caption='BMFTR supports FloodAdaptVN’s current implementation phase.',
        image_link='https://framefavn.org/')
rule(541)
project(560, '02 · African border crossings',
        'Trade Fluidity & Border Monitoring',
        'World Bank · Border Observatory',
        'Satellite-based vehicle-occupancy estimates support research on congestion, logistics '
        'and African trade. Explore historical border observations and Chirundu in 3D.',
        'chirundu-overview.webp', [
            ('Explore the Border Observatory', 'https://wbearthobservation.org/traffic/v11/?site=ID_004_Chirundu'),
            ('Reproducible research · World Bank', 'https://reproducibility.worldbank.org/catalog/667')],
        height=198, image_height=134,
        caption='The indicator estimates occupied area, not direct vehicle counts or crossing times.',
        image_link='https://wbearthobservation.org/traffic/v11/?site=ID_004_Chirundu')
page_footer(1, 'Portal previews: FRAME and Border Observatory. Chirundu basemap © OpenStreetMap contributors.')

# 2 — Climate reporting, open land data and method strengths.
page_header('Current work', 'Land information.<br/>Climate decisions.',
            'Open geospatial data, practical mapping and reproducible workflows.')
project(160, '03 · Ukraine / Black Sea region',
        'Paris Agreement & Black Sea Adaptation',
        'International Climate Initiative (IKI) · GIZ',
        'Supporting Ukraine in the implementation of the Paris Agreement and adaptation to the '
        'impact of climate change in the Black Sea region (PAABS).<br/><br/>'
        'My contribution: satellite-based land monitoring for greenhouse-gas reporting. '
        'The paabs.de research atlas makes this work accessible to project partners.',
        'paabs-platform.webp', [('paabs.de', 'https://paabs.de/')], height=261,
        image_height=169,
        caption='Sentinel-2, OpenStreetMap-derived training data and reproducible land-cover classification.',
        image_link='https://paabs.de/')
rule(437)
project(457, '04 · Europe / Heidelberg',
        'OSM Land Use',
        'Heidelberg University · HeiGIT',
        'European land-use information at 10-metre resolution, combining OpenStreetMap and Sentinel-2. '
        'I co-led the project with Alexander Zipf and contributed methods for filling mapping gaps '
        'using deep learning, with Hao Li and Zhaoyan Wu.',
        'osmlanduse-portal.webp', [
            ('osmlanduse.org', 'https://osmlanduse.org/'),
            ('Open dataset · heiDATA', 'https://doi.org/10.11588/data/IUTCDN')],
        height=219, image_height=145,
        caption='2020 reference year · Scientific Data, 2025.<br/>Map data © OpenStreetMap contributors.',
        image_link='https://osmlanduse.org/')
rule(691)
label('Methods that connect the work', M, 706)
paragraph('Satellite time series  ·  Machine learning  ·  OpenStreetMap<br/>'
          'Greenhouse-gas estimation  ·  Reproducible processing  ·  Interactive geospatial tools',
          M, 727, CW, 9.2, 14, color=MUTED)
page_footer(2, 'Programme names, funding context and full project credits: schultzheidelberg.github.io/projects/ and /sources/.')

# 3 — Earlier research and conservation experience.
page_header('Past work', 'Forests, carbon<br/>and conservation.',
            'Research and applied experience across tropical landscapes.')
project(158, '05 · Vietnam / Lao PDR · 2011–2020',
        'Forest Carbon & REDD+',
        'Jena · Wageningen · WWF / Österreichische Bundesforste',
        'Landsat observations and forest inventories supported estimates of carbon emissions and '
        'removals in Central Vietnam. For Xe Pian in Lao PDR, I contributed baseline analysis, '
        'reporting, validation and local training for REDD+ work under the Verified Carbon Standard.',
        'past-carbon-vietnam.webp', [('Carbon study · 2016', 'https://doi.org/10.1080/17583004.2016.1254009')],
        height=184, image_height=134, body_size=9.5,
        caption='Vietnam carbon map · Avitabile et al. (2016); Schultz (2018), Fig. 2.5.',
        image_link=URL+'projects/#xe-pian')
rule(355)
project(372, '06 · Tropical forests · 2016–2018',
        'Tropical Forest Monitoring',
        'PhD thesis · Wageningen University · 2018',
        'My doctoral research investigated tropical deforestation with Landsat time series and '
        'breakpoint detection. A 2016 study compared eight vegetation indices across Brazil, '
        'Ethiopia and Vietnam.',
        'past-vegetation-spider.webp', [('Doctoral thesis · Wageningen', 'https://doi.org/10.18174/454885')],
        height=157, image_height=95, body_size=9.5,
        caption='Relative index performance · Schultz et al. (2016); Schultz (2018), Fig. 4.7.',
        image_link=URL+'assets/past-vegetation-spider.webp')
rule(547)
project(563, '07 · Southern Africa · 2016–2018',
        'Kavango–Zambezi Monitoring',
        'WWF · Peace Parks Foundation',
        'Landsat forest and vegetation-change monitoring in the KAZA conservation area, combining '
        'field validation in Zambia and Namibia, operational processing workflows and local training.',
        'past-wwf-kaza.webp', [('Research paper · 2018', 'https://doi.org/10.3390/rs10111850')],
        height=148, image_height=87, body_size=9.5,
        caption='KAZA map · Schultz et al. (2018), Fig. 1.<br/>CC BY 4.0.',
        image_link='https://doi.org/10.3390/rs10111850')
rule(726)
paragraph('<b>Further greenhouse-gas research:</b> land-use carbon fluxes in Baden-Württemberg '
          'and street-level vehicle emissions in Berlin, both published in 2023.',
          M, 737, CW, 8.8, 12.3, color=MUTED)
page_footer(3, 'Original figure excerpts; data unchanged. Full studies and image credits: schultzheidelberg.github.io/sources/.')

# 4 — Selected publications and a clear contact point.
page_header('Selected publications & contact', 'Research you<br/>can build on.',
            'A selection of journal articles, alongside open data and applied tools.')
records = json.loads((ROOT / 'data' / 'publications.json').read_text(encoding='utf-8'))
by_doi = {r['doi']: r for r in records if r.get('doi')}
selections = [
    ('10.1016/j.srs.2025.100358', 'Taghi-Lou, B., Schultz, M., Braun, A. & Hochschild, V.'),
    ('10.1038/s41597-025-04703-8', 'Schultz, M., Li, H., et al.'),
    ('10.1007/s10661-023-11141-9', 'Ulrich, V., Schultz, M., Lautenbach, S. & Zipf, A.'),
    ('10.3390/rs10111850', 'Schultz, M., Shapiro, A., Clevers, J. G. P. W., Beech, C. & Herold, M.'),
    ('10.1016/j.jag.2016.06.020', 'Schultz, M., et al.'),
    ('10.1080/17583004.2016.1254009', 'Avitabile, V., Schultz, M., et al.'),
]
y = 155
for doi, authors in selections:
    record = by_doi[doi]
    label(str(record['year']), M, y, 40)
    tx, tw = M+49, CW-49
    y = paragraph(escape(record['title']), tx, y, tw, 9.6, 13.1, 'BodyBold')
    y = paragraph(escape(authors), tx, y+4, tw, 8.1, 11.2, color=MUTED)
    journal = f"{record['venue']}, {record['volume']}"
    if record.get('issue'): journal += f"({record['issue']})"
    if record.get('pages'): journal += f", {record['pages']}"
    y = paragraph(escape(journal)+'.', tx, y+2, tw, 8.1, 11.2, color=MUTED)
    y = linked('doi.org/'+doi, 'https://doi.org/'+doi, tx, y+2, tw, 7.8, 10.7)
    y += 12
    if doi != selections[-1][0]: rule(y-5, tx, tw)
if y > 665: raise ValueError(f'Publications extend too far: {y:.1f}')
rule(676)
paragraph('Let’s connect.', M, 692, CW, 21, 25, 'Display')
linked(EMAIL, 'mailto:'+EMAIL, M, 726, 280, 10.1, 14)
linked('schultzheidelberg.github.io', URL, M, 745, 280, 9.7, 13)
linked('Full publication list & downloads', URL+'publications/', M+302, 706, CW-302, 8.3, 12)
linked('ORCID 0000-0002-4813-090X', 'https://orcid.org/0000-0002-4813-090X', M+302, 729, CW-302, 8.3, 12)
linked('GitHub · schultzheidelberg', 'https://github.com/schultzheidelberg', M+302, 749, CW-302, 8.3, 12)
page_footer(4, 'Public portfolio · Research, collaboration and practical environmental decision support.')
c.save()
print(f'Created {OUTPUT} ({OUTPUT.stat().st_size / 1024:.0f} KiB), four A4 pages.')
