"""Render the public, verified bibliography without a browser-side data fetch."""

import json
from collections import Counter
from datetime import date
from html import escape
from urllib.parse import urlsplit


GROUPS = {
    'Journal article': 'Journal articles',
    'Book chapter': 'Books & chapters',
    'Edited proceedings': 'Books & chapters',
    'Conference paper': 'Conference contributions',
    'Conference abstract': 'Conference contributions',
    'Conference contribution': 'Conference contributions',
    'Conference presentation': 'Conference contributions',
    'Workshop paper': 'Conference contributions',
    'Report': 'Reports & briefs',
    'Report contribution': 'Reports & briefs',
    'Policy brief contribution': 'Reports & briefs',
    'Dataset': 'Datasets',
    'Doctoral thesis': 'Theses',
    'Master’s thesis': 'Theses',
    'Presentation': 'Presentations',
}
EXPORT_FORMATS = ('pdf', 'bib', 'csv', 'json', 'md')


def load_publications(path):
    records = json.loads(path.read_text(encoding='utf-8'))
    ids = [record['record_id'] for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError('Publication record IDs must be unique')
    for record in records:
        if record['verification'] != 'verified':
            raise ValueError(f"Unverified publication: {record['record_id']}")
        if record['publication_type'] not in GROUPS:
            raise ValueError(f"Add a display group for {record['publication_type']}")
    return sorted(records, key=lambda record: -record['year'])


def publication_venue(record):
    volume = str(record.get('volume', ''))
    if record.get('issue'):
        volume += f"({record['issue']})"
    return ' · '.join(str(part) for part in
                      (record['venue'], volume, record.get('pages')) if part)


def source_link(label, url):
    # Only public HTTPS sources become clickable; unsafe/staging URLs stay out.
    parsed = urlsplit(url)
    if parsed.scheme != 'https' or not parsed.netloc:
        return ''
    return f'<a href="{escape(url, quote=True)}">{escape(label)}</a>'


def render_record(record):
    title = record['title']
    venue = publication_venue(record)
    doi_url = 'https://doi.org/' + record['doi'] if record.get('doi') else ''
    main_url = record['landing_url'] or doi_url
    author_label = ('Presenter: ' if record.get('presenter_only') else '') + record['authors']
    citation = f"{author_label} ({record['year']}). {title}. {venue}."
    if doi_url:
        citation += ' ' + doi_url
    actions = [source_link('Source record ↗', main_url)]
    if doi_url:
        actions.append(source_link('Volume DOI ↗' if record.get('doi_scope') else 'DOI ↗', doi_url))
    pdf_url = record.get('pdf_url', '')
    pdf_label = 'Source PDF ↗'
    if 'thesis' in record.get('pdf_version', '').lower():
        pdf_url = record.get('alternate_pdf_url') or pdf_url
        pdf_label = 'Thesis PDF (includes study) ↗'
    if pdf_url:
        actions.append(source_link(pdf_label, pdf_url))
    actions.append(f'<button class="copy-citation" data-citation="{escape(citation, quote=True)}" '
                   f'aria-label="Copy citation for {escape(title, quote=True)}">Copy citation</button>')
    contributor = ''
    if record.get('contributors'):
        contributor = '<p class="pub-contribution">Contributor: Michael Schultz · not a principal author</p>'
    sources = ' · '.join(filter(None, (
        source_link(f'Source {index}', url)
        for index, url in enumerate(dict.fromkeys(record.get('evidence_urls', [])), 1)
    )))
    notes = escape(record.get('notes', ''))
    scope = '<p>The DOI identifies the complete volume, not this individual contribution.</p>' if record.get('doi_scope') else ''
    group = GROUPS[record['publication_type']]
    haystack = ' '.join(str(record.get(key, '')) for key in
                        ('title', 'authors', 'year', 'venue', 'doi', 'publication_type', 'contributors'))
    return f'''<article class="publication" id="{escape(record['record_id'])}" data-search="{escape(haystack, quote=True)}" data-type="{escape(group, quote=True)}" data-year="{record['year']}">
<time class="pub-year" datetime="{record['year']}">{record['year']}</time><div>
<p class="pub-type">{escape(record['publication_type'])}</p>
<h2>{source_link(title, main_url)}</h2>
<p class="pub-authors">{escape(author_label)}</p>{contributor}
<p class="pub-journal">{escape(venue)}</p>
<div class="pub-actions">{''.join(actions)}</div>
<details class="pub-evidence"><summary>Record notes &amp; sources</summary>
<p>Status: {escape(record['status'])}. Checked {escape(record['checked_on'])}.</p>{scope}
<p>{notes}</p><p class="evidence-links">{sources}</p>
</details></div></article>'''


def render_publications(records, metrics):
    total = len(records)
    journal_count = sum(record['publication_type'] == 'Journal article' for record in records)
    years = sorted({record['year'] for record in records}, reverse=True)
    checked = date.fromisoformat(max(record['checked_on'] for record in records))
    checked_label = f'{checked.day} {checked:%B %Y}'
    metrics_checked = date.fromisoformat(metrics['checked_on'])
    metrics_date_label = f'{metrics_checked.day} {metrics_checked:%B %Y}'
    if type(metrics['h_index']) is not int or metrics['h_index'] < 0:
        raise ValueError('h-index must be a non-negative integer')
    metric_source = source_link(metrics['source'], metrics['profile_url'])
    counts = Counter(GROUPS[record['publication_type']] for record in records)
    type_options = ''.join(f'<option value="{escape(group, quote=True)}">{escape(group)} ({counts[group]})</option>'
                           for group in dict.fromkeys(GROUPS.values()) if counts[group])
    year_options = ''.join(f'<option value="{year}">{year}</option>' for year in years)
    formats = {'pdf': 'PDF bibliography', 'bib': 'BibTeX', 'csv': 'CSV', 'json': 'JSON', 'md': 'Markdown'}
    downloads = ''.join(f'<a href="/downloads/publications.{extension}" download>{formats[extension]} ↓</a>'
                        for extension in EXPORT_FORMATS)
    return f'''
<div class="bibliography-overview">
<dl class="publication-stats"><div><dt>h-index · {metric_source}</dt><dd>{metrics['h_index']}</dd></div><div><dt>Verified research outputs</dt><dd>{total}</dd></div><div><dt>Journal articles</dt><dd>{journal_count}</dd></div><div><dt>Years of work</dt><dd>{min(years)}–{max(years)}</dd></div></dl>
<p class="subtle">h-index: {escape(metrics['source'])}, checked <time datetime="{metrics_checked.isoformat()}">{metrics_date_label}</time>. Citation metrics vary by database.</p>
<p class="subtle">Journal articles, chapters, datasets, reports, theses, and conference contributions. Editorial and contributor roles are labelled in each record. Last checked <time datetime="{checked.isoformat()}">{checked_label}</time>.</p>
</div>
<section class="bibliography-downloads" aria-labelledby="download-bibliography"><h2 id="download-bibliography">Take the bibliography with you</h2><p>Download the complete public inventory, with citations and source notes.</p><div class="download-links">{downloads}</div></section>
<div class="publication-tools" hidden>
<label class="search-field" for="publication-search"><span>Search the bibliography</span><input id="publication-search" type="search" placeholder="Title, author, topic, or DOI…" autocomplete="off" aria-controls="publication-list"></label>
<div class="publication-filters"><label for="publication-type">Output type<select id="publication-type" aria-controls="publication-list"><option value="">All outputs ({total})</option>{type_options}</select></label><label for="publication-year">Year<select id="publication-year" aria-controls="publication-list"><option value="">All years</option>{year_options}</select></label><button class="reset-filters" type="button">Clear filters</button></div>
</div>
<noscript><p class="subtle">All records are listed below, newest first. Use your browser’s Find command to search.</p></noscript>
<p class="publication-count" role="status" aria-live="polite">{total} research outputs · newest first</p>
<div class="publication-list" id="publication-list">{''.join(render_record(record) for record in records)}</div>
<p class="empty-result" hidden>No matching research outputs. Try another search or clear the filters.</p>
<p class="bibliography-footnote">Years follow the final journal issue or repository record; an earlier online date may differ. PDF links lead to publisher or repository copies; availability varies. Thesis alternatives and volume-level DOIs are labelled. See record notes for bibliographic corrections and access limitations.</p>'''


def render_work_in_progress(upcoming, manuscripts):
    """Keep accepted future talks and submitted manuscripts outside output totals."""
    output = ['<section class="section work-in-progress" id="upcoming"><h2>Upcoming conferences</h2><p class="subtle">Accepted contributions scheduled for December 2026. Listed separately from completed research outputs.</p>']
    for record in sorted(upcoming, key=lambda item: item['scheduled_date']):
        scheduled = date.fromisoformat(record['scheduled_date'])
        label = f'{scheduled.day} {scheduled:%B %Y}'
        output.append(f'''<article class="pending-record"><p class="work-status">Accepted · forthcoming poster</p>
<h3>{source_link(record['title'], record['landing_url'])}</h3>
<p class="pub-authors">{escape(record['authors'])}</p>
<p class="pub-journal">{escape(record['venue'])} · <time datetime="{scheduled.isoformat()}">{label}</time> · {escape(record['session_code'])}</p>
<p class="pub-actions">{source_link('Conference programme ↗', record['landing_url'])}</p></article>''')
    output.append('</section><section class="section work-in-progress" id="manuscripts"><h2>Manuscripts</h2><p class="subtle">Current submissions and revisions. These are not counted as published journal articles or included in the bibliography totals.</p>')
    for record in manuscripts:
        status_date = date.fromisoformat(record['status_date'])
        label = f'{status_date.day} {status_date:%B %Y}'
        output.append(f'''<article class="pending-record"><p class="work-status">{escape(record['status'])}</p>
<h3>{escape(record['title'])}</h3>
<p class="pub-authors">{escape(record['authors'])}</p>
<p class="pub-journal">{escape(record['venue'])}</p>
<p class="subtle">Latest confirmed status: <time datetime="{status_date.isoformat()}">{label}</time>.</p></article>''')
    output.append('</section>')
    return ''.join(output)
