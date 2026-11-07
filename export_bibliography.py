#!/usr/bin/env python3
"""Regenerate the public bibliography downloads from its JSON source.

Run ``python3 export_bibliography.py`` before ``python3 build.py`` after editing
data/publications.json. PDF export requires ReportLab and DejaVu Sans fonts;
the website build itself continues to use only the Python standard library.

For an isolated preview use ``--input /path/publications.json --output-dir /tmp/exports``.
Only the supplied public JSON is read. Separate manuscripts and upcoming-event
inventories are deliberately excluded. No network requests are made.
"""

import argparse
import csv
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote, urlsplit
from xml.sax.saxutils import escape, quoteattr


ROOT = Path(__file__).resolve().parent
ORCID = 'https://orcid.org/0000-0002-4813-090X'
TYPES = {
    'Journal article': 'article',
    'Book chapter': 'incollection',
    'Edited proceedings': 'proceedings',
    'Conference paper': 'inproceedings',
    'Workshop paper': 'inproceedings',
    'Conference abstract': 'misc',
    'Conference contribution': 'misc',
    'Conference presentation': 'misc',
    'Presentation': 'misc',
    'Report': 'techreport',
    'Report contribution': 'incollection',
    'Policy brief contribution': 'techreport',
    'Dataset': 'misc',
    'Doctoral thesis': 'phdthesis',
    'Master’s thesis': 'mastersthesis',
}
BASE_FIELDS = (
    'record_id', 'year', 'publication_type', 'title', 'authors', 'venue',
    'volume', 'issue', 'pages', 'doi', 'doi_scope', 'status', 'publication_date',
    'online_date', 'landing_url', 'pdf_url', 'pdf_version', 'license',
    'verification', 'notes', 'evidence_urls',
)


def load_records(path):
    records = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(records, list) or not records:
        raise ValueError('The public bibliography must be a non-empty JSON list')
    ids = set()
    for record in records:
        for key in ('record_id', 'title', 'authors', 'year', 'publication_type',
                    'venue', 'status', 'checked_on', 'verification'):
            if key not in record:
                raise ValueError(f'Missing required field: {key}')
        if record['record_id'] in ids:
            raise ValueError(f"Duplicate record ID: {record['record_id']}")
        ids.add(record['record_id'])
        if record['verification'] != 'verified':
            raise ValueError(f"Unverified record: {record['record_id']}")
        if record['publication_type'] not in TYPES:
            raise ValueError(f"Unsupported public output type: {record['publication_type']}")
        if type(record['year']) is not int:
            raise ValueError('Publication years must be integers')
        date.fromisoformat(record['checked_on'])
    return sorted(records, key=lambda r: (-r['year'], r['title'].casefold()))


def fields_for(records):
    extras = sorted(set().union(*(record.keys() for record in records)) - set(BASE_FIELDS))
    return list(BASE_FIELDS) + extras


def scalar(value):
    if isinstance(value, (list, dict, bool)) or value is None:
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def summary(records):
    checked = date.fromisoformat(max(r['checked_on'] for r in records))
    journals = sum(r['publication_type'] == 'Journal article' for r in records)
    return (f'{len(records)} verified research-output records, including {journals} '
            f'journal articles. Checked {checked.day} {checked:%B %Y}.')


def citation(record):
    volume = str(record.get('volume', ''))
    if record.get('issue'):
        volume += f"({record['issue']})"
    venue = ', '.join(str(x) for x in (record['venue'], volume, record.get('pages')) if x)
    names = record['authors']
    if presenter_only(record):
        names = f'Presenter: {names}'
    return f"{names} ({record['year']}). {record['title']}. {venue}."


def safe_url(url):
    if not isinstance(url, str):
        return ''
    parsed = urlsplit(url)
    if parsed.scheme not in ('https', 'http') or not parsed.netloc:
        return ''
    return quote(url, safe=":/?#[]@!$&'()*+,;=%~_-")


def record_links(record):
    links = []
    if record.get('doi'):
        links.append(('Volume DOI' if record.get('doi_scope') else 'DOI',
                      'https://doi.org/' + record['doi']))
    for key, label in (('landing_url', 'Source record'), ('pdf_url', 'Source PDF'),
                       ('alternate_pdf_url', 'Alternative PDF'),
                       ('additional_pdf_url', 'Additional PDF')):
        if record.get(key):
            links.append((label, record[key]))
    links.extend((f'Evidence {i}', url) for i, url in
                 enumerate(dict.fromkeys(record.get('evidence_urls', [])), 1))
    return [(label, safe_url(url)) for label, url in links if safe_url(url)]


def write_csv(records, path):
    # Retain the existing UTF-8 BOM so spreadsheets recognise Vietnamese names.
    with path.open('w', encoding='utf-8-sig', newline='') as output:
        writer = csv.DictWriter(output, fieldnames=fields_for(records), lineterminator='\n')
        writer.writeheader()
        for record in records:
            writer.writerow({key: scalar(value) for key, value in record.items()})


def markdown_text(value):
    return scalar(value).replace('\\', '\\\\').replace('|', '\\|').replace('\n', '<br>')


def write_markdown(records, path):
    lines = ['# Michael Schultz — verified publication inventory', '', summary(records),
             '', f'ORCID: {ORCID}', '',
             'Output types distinguish journal articles, chapters, conference contributions, '
             'reports, datasets, theses, and editorial or contributor roles. '
             'Manuscripts and forthcoming presentations are maintained separately.', '',
             'Years follow the final bibliographic issue or repository record. '
             'A volume DOI is labelled explicitly. Blank fields mean that information '
             'has not been established.', '']
    current_year = None
    fields = fields_for(records)
    for record in records:
        if record['year'] != current_year:
            current_year = record['year']
            lines.extend([f'## {current_year}', ''])
        lines.extend([f"### {record['record_id']} — {record['title']}", '',
                      citation(record), '',
                      ' · '.join(f'[{label}]({url})' for label, url in record_links(record)), '',
                      '| Field | Value |', '| --- | --- |'])
        # Every source field is retained, including dates, contributors and PDF variants.
        for key in fields:
            if key in record:
                lines.append(f'| {key} | {markdown_text(record[key])} |')
        lines.append('')
    path.write_text('\n'.join(lines), encoding='utf-8')


def bib_escape(value):
    replacements = {'\\': r'\textbackslash{}', '{': r'\{', '}': r'\}',
                    '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#',
                    '_': r'\_', '~': r'\textasciitilde{}', '^': r'\textasciicircum{}'}
    return ''.join(replacements.get(c, c) for c in scalar(value)).replace('\n', ' ')


def presenter_only(record):
    role = str(record.get('author_role', '')).lower()
    return (record.get('presenter_only') is True or role == 'presenter'
            or 'presenter only' in role or 'presenter-only' in role)


def write_bibtex(records, path):
    entries = []
    keys = set()
    for record in records:
        entry_type = TYPES[record['publication_type']]
        key = re.sub(r'[^A-Za-z0-9]', '', record['record_id'])
        if not key or key in keys:
            raise ValueError(f'Non-unique BibTeX key: {key}')
        keys.add(key)
        fields = {'title': record['title'], 'year': record['year'],
                  'record_id': record['record_id'], 'type': record['publication_type']}
        names = record['authors']
        if entry_type == 'proceedings':
            names = re.sub(r'\s*\(editors?\)', '', names, flags=re.I)
            fields['editor'] = ' and '.join(n.strip() for n in names.split(';'))
        elif not presenter_only(record):
            fields['author'] = ' and '.join(n.strip() for n in names.split(';'))
        venue_field = {'article': 'journal', 'incollection': 'booktitle',
                       'inproceedings': 'booktitle', 'techreport': 'institution',
                       'phdthesis': 'school', 'mastersthesis': 'school',
                       'proceedings': 'publisher'}.get(entry_type, 'howpublished')
        fields[venue_field] = record['venue']
        for source, target in (('volume', 'volume'), ('issue', 'number'), ('pages', 'pages'),
                               ('doi', 'doi'), ('landing_url', 'url'),
                               ('publication_date', 'date'), ('checked_on', 'urldate')):
            if record.get(source):
                value = record[source]
                if target == 'pages':
                    value = re.sub(r'(?<=\d)[–-](?=\d)', '--', str(value))
                fields[target] = value
        notes = [f"Status: {record['status']}."]
        if presenter_only(record):
            notes.append(f"Presenter: {names}. Complete author list not verified.")
        if record.get('contributors'):
            notes.append(f"Contributors: {record['contributors']}.")
        if record.get('doi_scope'):
            notes.append('DOI identifies the complete volume.')
        if record.get('online_date'):
            notes.append(f"Online date: {record['online_date']}.")
        if record.get('notes'):
            notes.append(record['notes'])
        fields['note'] = ' '.join(notes)
        lines = []
        for name, value in fields.items():
            # URL and DOI are literal identifiers, not TeX prose.
            encoded = str(value) if name in ('doi', 'url') else bib_escape(value)
            if name == 'title':
                encoded = '{' + encoded + '}'
            lines.append(f'  {name} = {{{encoded}}}')
        entries.append('@' + entry_type + '{' + key + ',\n' + ',\n'.join(lines) + '\n}')
    path.write_text('\n\n'.join(entries) + '\n', encoding='utf-8')


def write_pdf(records, path, font_dir):
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    for name, filename in (('Bibliography', 'DejaVuSans.ttf'),
                           ('BibliographyBold', 'DejaVuSans-Bold.ttf')):
        pdfmetrics.registerFont(TTFont(name, str(font_dir / filename)))
    pdfmetrics.registerFontFamily('Bibliography', normal='Bibliography',
                                  bold='BibliographyBold', italic='Bibliography',
                                  boldItalic='BibliographyBold')
    navy, muted = colors.HexColor('#16344b'), colors.HexColor('#526271')
    styles = {
        'cover': ParagraphStyle('Cover', fontName='BibliographyBold', fontSize=23,
                                leading=29, textColor=navy, spaceAfter=12),
        'year': ParagraphStyle('Year', fontName='BibliographyBold', fontSize=17,
                               leading=23, textColor=navy, spaceBefore=16,
                               spaceAfter=10, keepWithNext=True),
        'title': ParagraphStyle('Title', fontName='BibliographyBold', fontSize=10.5,
                                leading=14.2, textColor=navy, spaceBefore=12,
                                spaceAfter=5, keepWithNext=True),
        'body': ParagraphStyle('Body', fontName='Bibliography', fontSize=9,
                               leading=13, spaceAfter=5, alignment=TA_LEFT),
        'small': ParagraphStyle('Small', fontName='Bibliography', fontSize=8,
                                leading=11.5, textColor=muted, spaceAfter=5),
    }
    story = []

    def paragraph(text, style='body', markup=False):
        story.append(Paragraph(text if markup else escape(text), styles[style]))

    paragraph('Michael Schultz<br/>Research bibliography', 'cover', markup=True)
    paragraph(summary(records))
    paragraph('Journal articles, chapters, research data, reports, conference contributions '
              'and theses. Editorial and contributor roles are identified in each record.')
    paragraph('Manuscripts and forthcoming presentations are listed separately on the website '
              'and are excluded from this bibliography.', 'small')
    paragraph(f'<a href={quoteattr(ORCID)} color="#12628c">ORCID 0000-0002-4813-090X</a>'
              ' · <a href="https://schultzheidelberg.github.io/publications/" '
              'color="#12628c">Publications online</a>', 'small', markup=True)
    counts = Counter(r['publication_type'] for r in records)
    paragraph(' · '.join(f'{kind}: {count}' for kind, count in sorted(counts.items())), 'small')
    story.append(Spacer(1, 4 * mm))
    current_year = None
    for record in records:
        if record['year'] != current_year:
            current_year = record['year']
            paragraph(str(current_year), 'year')
        paragraph(record['title'], 'title')
        role = 'Presenter' if presenter_only(record) else ('Editors' if
               record['publication_type'] == 'Edited proceedings' else 'Authors')
        paragraph(f"{role}: {record['authors']}")
        volume = str(record.get('volume', ''))
        if record.get('issue'):
            volume += f"({record['issue']})"
        paragraph(' · '.join(str(x) for x in (record['venue'], volume,
                                             record.get('pages')) if x))
        paragraph(f"{record['record_id']} · {record['publication_type']} · "
                  f"{record['status']} · Checked {record['checked_on']}", 'small')
        if record.get('contributors'):
            paragraph(f"Contributors: {record['contributors']}", 'small')
        for field, label in (('publication_date', 'Publication date'),
                              ('online_date', 'First online'), ('license', 'Licence')):
            if record.get(field):
                paragraph(f'{label}: {record[field]}', 'small')
        if record.get('doi'):
            paragraph(('Volume DOI: ' if record.get('doi_scope') else 'DOI: ')
                      + record['doi'], 'small')
        if record.get('notes'):
            paragraph(record['notes'], 'small')
        links = ' · '.join(f'<a href={quoteattr(url)} color="#12628c">{escape(label)}</a>'
                           for label, url in record_links(record))
        if links:
            paragraph(links, 'small', markup=True)

    def footer(canvas, document):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor('#d8e0e5'))
        canvas.line(19 * mm, 16 * mm, A4[0] - 19 * mm, 16 * mm)
        canvas.setFillColor(muted)
        canvas.setFont('Bibliography', 7)
        canvas.drawString(19 * mm, 11 * mm, 'Michael Schultz · Verified research bibliography')
        canvas.drawRightString(A4[0] - 19 * mm, 11 * mm, str(document.page))
        canvas.restoreState()

    document = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=19 * mm,
                                 leftMargin=19 * mm, topMargin=18 * mm,
                                 bottomMargin=23 * mm, title='Michael Schultz — Research bibliography',
                                 author='Michael Schultz')
    document.build(story, onFirstPage=footer, onLaterPages=footer)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=ROOT / 'data/publications.json')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'data')
    parser.add_argument('--font-dir', type=Path,
                        default=Path('/usr/share/fonts/truetype/dejavu'))
    args = parser.parse_args()
    records = load_records(args.input)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    # Prepare every output first so a font/PDF error leaves existing exports intact.
    with TemporaryDirectory(prefix='.bibliography-export-', dir=args.output_dir) as temp:
        temporary = Path(temp)
        write_csv(records, temporary / 'publications.csv')
        write_markdown(records, temporary / 'publications.md')
        write_bibtex(records, temporary / 'publications.bib')
        write_pdf(records, temporary / 'publications.pdf', args.font_dir)
        for extension in ('csv', 'md', 'bib', 'pdf'):
            name = f'publications.{extension}'
            (temporary / name).replace(args.output_dir / name)
    print(f'Exported {len(records)} records to CSV, Markdown, BibTeX and PDF in {args.output_dir}')


if __name__ == '__main__':
    main()
