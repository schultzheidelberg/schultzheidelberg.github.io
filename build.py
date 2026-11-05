"""Build a small, portable academic website using only the Python standard library."""
from pathlib import Path
from html import escape as e
from shutil import copytree, copyfile
from bibliography import EXPORT_FORMATS, load_publications, publication_venue, render_publications

ROOT = Path(__file__).parent
DIST = ROOT / 'docs'
ORIGIN = 'https://schultzheidelberg.github.io'
EMAIL = 'schultz.consulting@outlook.com'
GITHUB = 'https://github.com/schultzheidelberg'
REPO = GITHUB + '/OpenStreetMap-land-use-for-Europe-2020'
ORCID = 'https://orcid.org/0000-0002-4813-090X'
LINKEDIN = 'https://de.linkedin.com/in/michael-schultz-a9025638'
PROFILE = 'https://uni-tuebingen.de/en/fakultaeten/mathematisch-naturwissenschaftliche-fakultaet/fachbereiche/geowissenschaften/arbeitsgruppen/geographie/forschungsbereich/geoinformatik-gis/arbeitsgruppe/team/michael-schultz/'
INSTITUTIONAL_PUBS = 'https://uni-tuebingen.de/en/fakultaeten/mathematisch-naturwissenschaftliche-fakultaet/fachbereiche/geowissenschaften/arbeitsgruppen/geographie/forschungsbereich/geoinformatik-gis/arbeitsgruppe/publikationen/'
DATA = 'https://doi.org/10.11588/data/IUTCDN'
PAPER = 'https://doi.org/10.1038/s41597-025-04703-8'
THESIS = 'https://doi.org/10.18174/454885'
FRAME = 'https://framefavn.org/frame/'
FRAME_VN = 'https://frame-vn.org/frame/'
FLOODADAPT = 'https://floodadapt.eoc.dlr.de/index.html'
PAABS = 'https://www.giz.de/en/projects/implementation-paris-agreement-ukrainepaabs'
WBEO = 'https://wbearthobservation.org/traffic/v11/'

ICONS = {
 'arrow':'<path d="M4 12h16m-6-6 6 6-6 6"/>',
 'external':'<path d="M14 3h7v7M21 3 10 14"/><path d="M10 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-5"/>',
 'pin':'<path d="M20 10c0 6-8 11-8 11S4 16 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/>',
 'mail':'<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 6 9 7 9-7"/>',
 'github':'<path d="M9 19c-4 1-4-2-6-2m12 5v-4a3.5 3.5 0 0 0-1-2.7c3.4-.4 7-1.7 7-7.3a5.7 5.7 0 0 0-1.6-4c.2-1.3.2-2.7-.4-4 0 0-1.3-.4-4.3 1.6a15 15 0 0 0-7.4 0C4.3-.4 3 0 3 0c-.6 1.3-.6 2.7-.4 4A5.7 5.7 0 0 0 1 8c0 5.6 3.6 6.9 7 7.3A3.5 3.5 0 0 0 7 18v4" transform="translate(2 1) scale(.88)"/>',
 'id':'<circle cx="12" cy="12" r="9"/><path d="M7.5 10v7m0-10v.1M11 7h2a5 5 0 0 1 0 10h-2Z"/>',
 'linkedin':'<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M7 10v7m0-10v.1M11 17v-7m0 3a3 3 0 0 1 6 0v4"/>',
 'book':'<path d="M12 5c-3-2-6-2-10-1v15c4-1 7-1 10 1 3-2 6-2 10-1V4c-4-1-7-1-10 1Zm0 0v15"/>',
 'search':'<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
 'menu':'<path d="M4 6h16M4 12h16M4 18h16"/>',
 'print':'<path d="M6 9V3h12v6M6 17H3V9h18v8h-3M6 14h12v7H6Z"/>'
}
def icon(name): return f'<svg viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'
def link(label, url, cls='arrow-link', external=False):
    return f'<a class="{cls}" href="{e(url, quote=True)}">{label}{icon("external" if external else "arrow")}</a>'
def heading(title, intro, eyebrow='EARTH OBSERVATION & OPEN SCIENCE'):
    return f'<header class="page-heading"><div class="eyebrow">{eyebrow}</div><h1>{title}</h1><p class="intro">{intro}</p></header>'

PUBLICATIONS = load_publications(ROOT / 'data' / 'publications.json')

credit = '<p class="image-credit"><a href="https://www.nature.com/articles/s41597-025-04703-8/figures/2">Schultz et al. (2025), Fig. 2</a> · <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>. Map data © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>.</p>'
feature = f'''<div class="feature"><a class="feature-visual" href="/projects/#osmlanduse" aria-label="Explore the OSMlanduse project"><img src="/assets/osmlanduse-map.webp" width="1900" height="1345" alt="OSMlanduse research figure showing land-use maps of Europe and detailed regional comparisons" loading="lazy"></a><div class="feature-copy"><span class="tag">FEATURED PROJECT · OPEN DATA</span><h3>Europe, at 10 metres.</h3><p>OSMlanduse brings OpenStreetMap and Sentinel-2 together to map land use across the European Union.</p>{link('Explore OSMlanduse','/projects/#osmlanduse')}</div></div>{credit}'''

frame_feature = f'''<div class="feature frame-feature"><a class="feature-visual" href="{FRAME}" aria-label="Open the FRAME flood-risk platform"><img src="/assets/frame-scenarios.png" alt="FRAME illustration of comparing flood and urban-growth scenarios" loading="lazy"></a><div class="feature-copy"><span class="tag">FRAME · HUẾ, VIETNAM</span><h3>Making flood risk<br>easier to explore.</h3><p>Maps and scenario tools connecting flood-risk research with local planning.</p><div class="project-links">{link('English portal',FRAME,external=True)}{link('Tiếng Việt',FRAME_VN,external=True)}</div></div></div><p class="image-credit">Project illustration from <a href="{FRAME}">FRAME / FloodAdaptVN</a>.</p>'''

about = heading('From space to<br>better decisions.', 'I turn satellite observations into useful maps, open data, and tools for understanding a changing world.', 'ABOUT · MICHAEL SCHULTZ') + f'''
<div class="body-copy"><p>I’m Michael Schultz, an earth observation researcher based in <strong>Reutlingen, Germany</strong>. My work brings together remote sensing, machine learning, and open geospatial information.</p><p>My projects span flood-risk planning in Vietnam, land monitoring in Ukraine, and satellite-based observations of African border crossings. The common thread: making complex environmental information useful beyond the research paper.</p></div>
<div class="inline-links">{link('Explore my projects','/projects/')}{link('Get in touch','/contact/')}</div>
<section class="section" aria-labelledby="featured"><div class="section-top"><h2 id="featured">Research you can explore</h2>{link('About FRAME','/projects/#frame')}</div>{frame_feature}</section>
<section class="section" aria-labelledby="themes"><div class="section-top"><h2 id="themes">Recent work & open projects</h2>{link('All projects','/projects/')}</div><ul class="theme-list">
<li><a href="/projects/#ukraine"><span class="theme-num">01</span><div><h3>Ukraine · Land monitoring for climate reporting</h3><p>Contributing satellite-based land-use mapping to the PAABS programme.</p></div>{icon('arrow')}</a></li>
<li><a href="/projects/#border-observatory"><span class="theme-num">02</span><div><h3>Africa · Border Observatory</h3><p>An interactive view of historical occupied-area observations at border crossings.</p></div>{icon('arrow')}</a></li>
<li><a href="/projects/#osmlanduse"><span class="theme-num">03</span><div><h3>Europe · OSMlanduse</h3><p>OpenStreetMap and Sentinel-2, brought together in a 10-metre land-use map.</p></div>{icon('arrow')}</a></li>
</ul></section>
<section class="section" aria-labelledby="recent"><div class="section-top"><h2 id="recent">Selected publications</h2>{link('View publications','/publications/')}</div>'''
for doi in ('10.1016/j.srs.2025.100358', '10.1038/s41597-025-04703-8'):
    p = next(record for record in PUBLICATIONS if record['doi'] == doi)
    about += f'<article class="publication-preview"><time>{p["year"]}</time><div><h3><a href="https://doi.org/{p["doi"]}">{e(p["title"])}</a></h3><p>{e(publication_venue(p))}</p></div></article>'
about += f'<p class="subtle bibliography-home">Explore <a href="/publications/">{len(PUBLICATIONS)} verified research outputs</a>, including {sum(p["publication_type"] == "Journal article" for p in PUBLICATIONS)} journal articles, with citations and bibliography downloads.</p></section>'

research = heading('Research', 'Connecting observations, methods, and environmental questions.') + f'''
<div class="body-copy"><p>My research spans open land-use mapping, satellite time-series analysis, and the use of geospatial information to understand environmental risk.</p></div>
<section class="detail-section" id="land-use"><span class="tag">01 · LAND USE & OPEN DATA</span><h2>Combining satellite data with local knowledge</h2><p>Satellite imagery records the physical landscape. OpenStreetMap adds information about how people use it. My research explores how these sources can work together, including through machine learning, to produce detailed land-use information.</p><p>The OSMlanduse project applies this approach across Europe using Sentinel-2 observations and OpenStreetMap. My more recent work contributes land-use and land-cover mapping to Ukraine’s PAABS programme.</p><div class="inline-links">{link('OSMlanduse','/projects/#osmlanduse')}{link('Ukraine PAABS','/projects/#ukraine')}{link('Read the paper',PAPER,external=True)}</div></section>
<section class="detail-section" id="forest-change"><span class="tag">02 · FOREST CHANGE</span><h2>Reading change through time</h2><p>Long satellite records make it possible to study how forests change. My doctoral work at Wageningen University investigated tropical deforestation monitoring using Landsat time series and breakpoint detection.</p><p>This work included studying how vegetation indices perform when detecting deforestation.</p><div class="inline-links">{link('Doctoral thesis',THESIS,external=True)}{link('Related publication','https://doi.org/10.1016/j.jag.2016.06.020',external=True)}</div></section>
<section class="detail-section" id="risk"><span class="tag">03 · RISK & ADAPTATION</span><h2>Environmental information for decisions</h2><p>My work also addresses environmental hazards. FRAME makes flood scenarios and adaptation information explorable through web tools for Huế and Central Vietnam. A separate collaborative study uses Sentinel-1 interferometry to examine ground deformation after the March 2025 earthquake in Mandalay, Myanmar.</p><div class="inline-links">{link('Explore FRAME',FRAME,external=True)}{link('Vietnam project overview','/projects/#frame')}{link('Mandalay study','https://doi.org/10.1016/j.srs.2025.100358',external=True)}</div></section>'''

projects = heading('Projects', 'From flood resilience in Vietnam to land monitoring in Ukraine: research, platforms, and open data you can explore.') + f'''
<nav class="project-index" aria-label="Jump to a project"><a href="#frame">FRAME · Vietnam</a><a href="#ukraine">PAABS · Ukraine</a><a href="#border-observatory">Border Observatory</a><a href="#osmlanduse">OSMlanduse</a></nav>
<section class="project" id="frame"><span class="tag">FLOOD RESILIENCE · HUẾ, VIETNAM</span><h2>FRAME & FloodAdaptVN</h2><p>How can flood-risk research become something people can explore and use? My work on FRAME connects geospatial data, flood scenarios, and accessible web tools for Huế and Central Vietnam.</p><p>The platform is part of FloodAdaptVN, a German–Vietnamese collaboration linking flood-risk research with adaptation planning. Its current implementation phase runs from June 2025 to May 2027.</p><div class="project-links">{link('FRAME · English',FRAME,external=True)}{link('FRAME · Tiếng Việt',FRAME_VN,external=True)}{link('FloodAdaptVN project',FLOODADAPT,external=True)}</div>
<div class="tool-grid">
<a href="{FRAME}scenario-explorer/"><span class="tag">EXPLORE SCENARIOS</span><h3>How might risk change?</h3><p>Compare flood depths and urban-growth scenarios for 2030 and 2050.</p><span class="tool-action">Open scenario explorer {icon('external')}</span></a>
<a href="{FRAME}flood-adaptation-products/"><span class="tag">EXPLORE ADAPTATION</span><h3>What can we do?</h3><p>Explore ecosystem-based adaptation, adaptation economics, water quality, and parking guidance.</p><span class="tool-action">Browse FRAME tools {icon('external')}</span></a>
</div><p class="project-meta">Planning and research tools based on historical observations and modelled scenarios.</p><div class="project-links">{link('How FRAME works','https://elib.dlr.de/217324/',external=True)}{link('Project updates','https://floodadapt.eoc.dlr.de/news/index.html',external=True)}</div></section>
<section class="project" id="ukraine"><span class="tag">LAND MONITORING · UKRAINE · 2025–PRESENT</span><h2>PAABS: mapping land for climate reporting</h2><p>Since October 2025, I have contributed to the PAABS programme’s land-monitoring work in Ukraine. In 2026, I coordinated land-use and land-cover classification combining Sentinel-2 observations, OpenStreetMap-derived training data, and reproducible processing workflows.</p><p>The work supports Ukraine’s Land Parcel Identification System and land-use, land-use-change and forestry reporting. It connects detailed satellite mapping with the information needed for climate policy.</p><div class="project-links">{link('PAABS programme · GIZ',PAABS,external=True)}{link('My contribution',LINKEDIN,external=True)}</div></section>
<section class="project" id="border-observatory"><span class="tag">EARTH OBSERVATION · AFRICA · RESEARCH PREVIEW</span><h2>Border Observatory</h2><p>Move from an Africa-wide overview to individual border crossings, then explore how estimated occupied area varies across the observation archive. This interactive viewer connects map features with historical satellite-derived summaries.</p><p class="project-meta">The indicator measures estimated occupied area; it does not directly measure vehicle counts, queues, or crossing times.</p><div class="project-links">{link('Open Border Observatory',WBEO,external=True)}{link('WBEO catalogue','https://wbearthobservation.org/catalogue/',external=True)}</div></section>
''' + f'''
<section class="project" id="osmlanduse"><span class="tag">LAND USE · EUROPE</span><h2>OSMlanduse</h2><p>A 10-metre land-use dataset combining OpenStreetMap and Sentinel-2. The project connects volunteered geographic information with satellite observations and deep learning to map land use across the European Union.</p><p class="project-meta">2020 reference year · Published in Scientific Data, 2025 · Joint first authors: Michael Schultz and Hao Li</p><div class="project-links">{link('Explore the map','https://osmlanduse.org',external=True)}{link('Get the data',DATA,external=True)}{link('Source code',REPO,external=True)}{link('Paper',PAPER,external=True)}</div><figure class="project-figure"><a href="https://www.nature.com/articles/s41597-025-04703-8/figures/2"><img src="/assets/osmlanduse-map.webp" width="1900" height="1345" alt="European land-use map and regional comparisons from the OSMlanduse study" loading="lazy"></a><figcaption>{credit}</figcaption></figure></section>
<section class="project" id="forest-monitoring"><span class="tag">SATELLITE TIME SERIES · TROPICAL FORESTS</span><h2>Tropical deforestation monitoring</h2><p>Doctoral research on detecting forest change from Landsat time series, with a focus on breakpoint detection and the performance of vegetation indices.</p><p class="project-meta">Doctoral thesis · Wageningen University, 2018</p><div class="project-links">{link('Explore the thesis',THESIS,external=True)}</div></section>'''

publications = heading('Publications', 'Research on land use, environmental change, and geospatial methods — from journal articles to open data and practical tools.')
publications += render_publications(PUBLICATIONS)
publications += f'<div class="inline-links">{link("ORCID profile",ORCID,external=True)}{link("ResearchGate","https://www.researchgate.net/profile/Michael-Schultz-6",external=True)}</div>'

code = heading('Code', 'Open research workflows, from observations to land-use information.') + f'''
<section class="resource"><span class="tag">FEATURED REPOSITORY</span><h2>OpenStreetMap land use for Europe</h2><p>Source code for the OSM4EO deep-learning workflow, including training-sample preparation, model training, classification, and post-processing.</p><div class="resource-details"><span>Python</span><span>Deep learning</span><span>Sentinel-2</span><span>OpenStreetMap</span><span>GPL-3.0</span></div>{link('View repository',REPO,external=True)}</section>
<section class="resource"><span class="tag">GITHUB</span><h2>More code & contributions</h2><p>Browse my public repositories and contributions on GitHub.</p><div class="inline-links">{link('@schultzheidelberg',GITHUB,external=True)}</div></section>
<section class="section"><div class="body-copy"><p>For the dataset and publication associated with OSMlanduse, visit the <a href="/data/">data page</a>.</p></div></section>'''

data = heading('Data', 'Open datasets that make research accessible and reusable.') + f'''
<section class="resource"><span class="tag">OPEN DATA · LAND USE</span><h2>OSMlanduse</h2><p>European land-use information derived from OpenStreetMap and Sentinel-2. The associated publication describes a dataset at 10-metre resolution.</p><div class="resource-details"><span>Europe</span><span>10 m</span><span>2020 reference year</span><span>Sentinel-2 + OSM</span><span>heiDATA</span></div><div class="project-links">{link('Dataset & downloads',DATA,external=True)}{link('Interactive map','https://osmlanduse.org',external=True)}{link('Data paper',PAPER,external=True)}</div></section>
<section class="section"><div class="section-top"><h2>From observation to information</h2></div>{feature}</section>
<section class="resource"><span class="tag">PROJECT CATALOGUES & VIEWERS</span><h2>Explore the wider work</h2><p>FRAME brings together flood scenarios and adaptation evidence for Vietnam. WBEO provides a catalogue of geospatial resources and an interactive Border Observatory.</p><div class="project-links">{link('FRAME platform',FRAME,external=True)}{link('WBEO catalogue','https://wbearthobservation.org/catalogue/',external=True)}{link('Border Observatory',WBEO,external=True)}</div></section>
<section class="detail-section"><h2>Using the data</h2><p>The heiDATA record provides the files, version information, and applicable reuse terms. Please cite the dataset and associated publication when using this work.</p><div class="inline-links">{link('View source code','/code/')}</div></section>'''

cv = heading('Background', 'Selected academic background and research experience.', 'CURRICULUM VITAE') + f'''
<div class="cv-actions"><button class="button" data-print>{icon('print')}Print / save as PDF</button>{link('ORCID record',ORCID,external=True)}</div>
<section class="section"><h2>Current project focus</h2><div class="body-copy"><p style="margin-top:16px">Based in Reutlingen, Germany, I work across satellite-based land monitoring, open geospatial information, and environmental decision-support tools.</p></div><div class="inline-links">{link('FRAME · Vietnam','/projects/#frame')}{link('PAABS · Ukraine','/projects/#ukraine')}{link('Border Observatory','/projects/#border-observatory')}</div></section>
<div class="timeline"><section class="timeline-item"><span class="timeline-label">2018 · PhD</span><div><h3>Wageningen University</h3><p>Tropical deforestation monitoring using Landsat time series and breakpoint detection.</p><p>Doctorate awarded 15 October 2018.</p>{link('Doctoral thesis',THESIS,external=True)}</div></section>
<section class="timeline-item"><span class="timeline-label">RESEARCH</span><div><h3>Remote sensing & volunteered geographic information</h3><p>Postdoctoral work at Heidelberg combining satellite observations with volunteered geographic information, including OpenStreetMap.</p>{link('Institutional biography',PROFILE,external=True)}</div></section>
<section class="timeline-item"><span class="timeline-label">RESEARCH</span><div><h3>Flood risk & adaptation</h3><p>Research associated with FloodAdaptVN and the FRAME flood-risk information system for Central Vietnam.</p>{link('FRAME chapter','https://doi.org/10.34712/142.70',external=True)}</div></section></div>
<section class="section"><h2>Research areas</h2><div class="resource-details"><span>Earth observation</span><span>Land-use mapping</span><span>Satellite time series</span><span>OpenStreetMap</span><span>Machine learning</span><span>Environmental risk</span></div></section>
<section class="section"><h2>Selected publications</h2><div class="body-copy"><p style="margin-top:16px">A selection of journal articles and contributions is available on the <a href="/publications/">publications page</a>. Further bibliographic information is linked through <a href="{ORCID}">ORCID</a>.</p></div></section>'''

contact = heading('Contact', 'Let’s connect around earth observation, geospatial research, and open data.') + f'''
<p class="contact-lead">Based in Reutlingen.<br>Working across borders.</p><p class="body-copy" style="margin-bottom:24px">For research collaborations and conversations about earth observation, open data, and geospatial tools.</p><a class="contact-email" href="mailto:{EMAIL}">{EMAIL}</a>
<div class="contact-grid">{link('GitHub',GITHUB,external=True)}{link('LinkedIn',LINKEDIN,external=True)}{link('ORCID',ORCID,external=True)}{link('ResearchGate','https://www.researchgate.net/profile/Michael-Schultz-6',external=True)}{link('FRAME · English',FRAME,external=True)}{link('FRAME · Tiếng Việt',FRAME_VN,external=True)}{link('Border Observatory',WBEO,external=True)}{link('WBEO catalogue','https://wbearthobservation.org/catalogue/',external=True)}</div>
<section class="section"><div class="body-copy"><p>Interested in a particular project? The <a href="/projects/">project pages</a> link directly to the relevant publications, code, and datasets.</p></div></section>'''

sources = heading('Sources & credits', 'Research records and image credits for this website.', 'ABOUT THIS SITE') + f'''
<div class="body-copy"><p>Academic and project information is drawn from the linked research records, project websites, and my professional profile. The project overview was updated in November 2026.</p></div><ul class="source-list"><li><a href="{PROFILE}">University of Tübingen — Michael Schultz’s research profile and portrait</a></li><li><a href="{THESIS}">Wageningen University — doctoral thesis, 2018</a></li><li><a href="{INSTITUTIONAL_PUBS}">University of Tübingen — Geoinformatics publications</a></li><li><a href="{PAPER}">Schultz et al. — OSMlanduse, Scientific Data, 2025</a></li><li><a href="{ORCID}">ORCID — Michael Schultz</a></li><li><a href="{REPO}">OSMlanduse code repository</a></li><li><a href="{FRAME}">FRAME — English portal</a> · <a href="{FRAME_VN}">Vietnamese portal</a></li><li><a href="{FLOODADAPT}">FloodAdaptVN — project and implementation period</a></li><li><a href="https://elib.dlr.de/217324/">DLR — FRAME chapter and complete author list</a></li><li><a href="{PAABS}">GIZ — PAABS programme in Ukraine</a></li><li><a href="{LINKEDIN}">My LinkedIn profile — Ukraine project contribution</a></li><li><a href="{WBEO}">Border Observatory — historical observation viewer</a></li></ul>
<section class="detail-section"><h2>Images</h2><p>The portrait is sourced from the University of Tübingen’s institutional profile. The OSMlanduse figure is reproduced unchanged from the open-access publication. The scenario illustration comes from the <a href="{FRAME}">FRAME / FloodAdaptVN platform</a>.</p>{credit}</section>
<section class="detail-section"><h2>Design inspiration</h2><p>The site’s academic structure was inspired by <a href="https://simonbesnard1.github.io/">Simon Besnard’s personal website</a>. This implementation is an independent, lightweight static website.</p></section>'''

PAGES = {'':('About',about),'research':('Research',research),'projects':('Projects',projects),'publications':('Publications',publications),'code':('Code',code),'data':('Data',data),'cv':('CV',cv),'contact':('Contact',contact),'sources':('Sources & credits',sources)}

def shell(key,title,body):
    page_url = ORIGIN + ('/404.html' if key == '404' else '/' + (key + '/' if key else ''))
    nav=''.join(f'<a href="/{slug + "/" if slug else ""}"'+(' aria-current="page"' if key==slug else '')+f'>{label}</a>' for slug,(label,_) in PAGES.items() if slug!='sources')
    profile_links=''.join(f'<a href="{url}">{icon(ic)}<span>{label}</span></a>' for ic,label,url in [('mail','Email','mailto:'+EMAIL),('github','GitHub',GITHUB),('id','ORCID',ORCID),('linkedin','LinkedIn',LINKEDIN),('book','ResearchGate','https://www.researchgate.net/profile/Michael-Schultz-6')])
    desc='Michael Schultz, based in Reutlingen, Germany — earth observation, FRAME flood-risk tools for Vietnam, land monitoring in Ukraine, and open geospatial data.'
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)} — Michael Schultz</title><meta name="description" content="{desc}"><meta name="theme-color" content="#172a32"><link rel="canonical" href="{page_url}"><meta property="og:title" content="{e(title)} — Michael Schultz"><meta property="og:description" content="{desc}"><meta property="og:type" content="website"><meta property="og:url" content="{page_url}"><meta property="og:image" content="{ORIGIN}/assets/michael-schultz.webp"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/site.css"><script src="/assets/site.js" defer></script></head>
<body><a class="skip" href="#main">Skip to content</a><header class="masthead"><div class="topbar"><a class="brand" href="/"><span class="brand-dot"></span>Michael Schultz</a><button class="menu-toggle" aria-expanded="false" aria-controls="navigation">{icon('menu')}Menu</button><nav id="navigation" class="nav" aria-label="Main navigation">{nav}</nav></div></header>
<div class="site-shell"><aside class="profile" aria-label="Michael Schultz’s profile"><div class="portrait-wrap"><img class="portrait" src="/assets/michael-schultz.webp" width="146" height="146" alt="Michael Schultz"></div><p class="profile-name">Dr. Michael Schultz</p><p class="profile-role">Earth observation &<br>geospatial research</p><p class="profile-location">{icon('pin')}Reutlingen, Germany</p><div class="profile-links">{profile_links}</div><a class="profile-contact" href="/contact/">Get in touch{icon('arrow')}</a><p class="profile-note">Satellite observations.<br>Open information.</p></aside><main class="page" id="main">{body}</main></div>
<footer class="site-footer"><div class="footer-inner"><span>© 2026 Michael Schultz</span><div class="footer-links"><a href="/sources/">Sources & credits</a><a href="{GITHUB}">GitHub ↗</a><a href="/contact/">Contact</a></div></div></footer><div class="status-message" role="status" aria-live="polite"></div></body></html>'''

DIST.mkdir(exist_ok=True)
copytree(ROOT / 'assets', DIST / 'assets', dirs_exist_ok=True)
(DIST / 'downloads').mkdir(exist_ok=True)
for extension in EXPORT_FORMATS:
    copyfile(ROOT / 'data' / f'publications.{extension}', DIST / 'downloads' / f'publications.{extension}')
(DIST / '.nojekyll').write_text('', encoding='utf-8')

for key,(title,body) in PAGES.items():
    folder=DIST/key
    folder.mkdir(exist_ok=True,parents=True)
    (folder/'index.html').write_text(shell(key,title,body),encoding='utf-8')

(DIST/'assets'/'favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40"><rect width="40" height="40" rx="8" fill="#172a32"/><text x="20" y="28" text-anchor="middle" fill="#fafaf7" font-family="Georgia,serif" font-size="25">M</text><circle cx="32" cy="9" r="3" fill="#91b59a"/></svg>')
(DIST/'404.html').write_text(shell('404','Page not found',heading('Page not found','This page may have moved.')+link('Return to About','/')),encoding='utf-8')
(DIST/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{ORIGIN}/{k+"/" if k else ""}</loc></url>' for k in PAGES)+'</urlset>')
(DIST/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {ORIGIN}/sitemap.xml\n')
print(f'Built {len(PAGES)} pages, plus 404, sitemap, and favicon.')
