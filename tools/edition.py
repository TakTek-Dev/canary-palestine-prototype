"""Compose tools/edition.json and tools/photos.json for Tuesday 20 October 2026 from the sourced research.

python -I tools/edition.py   (reads research/news.json + research/photos.json, both gitignored)

Every reading, date and source comes from research/news.json, where each item was checked against the
page it links to. This file only decides the network: which items make up which station, the lead,
the reporting and which photo sits where. A photo goes only where it shows that place or that kind of
thing, and its caption says what it is and when it was taken.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N = {i['id']: i for i in json.load(open(os.path.join(ROOT, 'research', 'news.json'), encoding='utf-8'))}
P = {p['file']: p for p in json.load(open(os.path.join(ROOT, 'research', 'photos.json'), encoding='utf-8'))}

# ---------------------------------------------------------------- photos
# slug -> (Commons file, year, caption, alt)
PHOTO = {
    'kh-pumps': ('File:Water supply in West Bank and Gaza February 2014 4water photoblog.jpg', '2014', 'Khan Younis, Gaza Strip',
                 'Pipes, valves and a pump inside a Water Authority pumping facility in Khan Younis.',
                 'Red and blue pipes, valves and a pump over a concrete pit inside a water facility'),
    'mawasi': ('File:An aerial view of Al-Mawasi area where displaced Palestinians live in tents, Gaza Strip.jpg', '2025', 'al-Mawasi, Khan Younis',
               'Tents of displaced families across al-Mawasi, Khan Younis, seen from the air in January 2025.',
               'Aerial view of a dense tent camp on sand stretching to the horizon'),
    'wadi-gaza': ('File:وادي غزة.jpg', '2025', 'Wadi Gaza',
                  'Wadi Gaza at sunset, January 2025: the low ground the winter rains flood first.',
                  'A channel of water winding through flat dark ground at sunset'),
    'wadi-gaza-2': ('File:Gaza Valley Gaza war 23-25.jpg', '2024', 'Wadi Gaza',
                    'Open water along Wadi Gaza, September 2024. Not a sampling site.',
                    'A narrow stream with reeds on its bank and trees behind'),
    'shifa': ('File:Al-Shifa Hospital in Gaza after Gaza war 23-25.jpg', '2025', 'al-Shifa Medical Complex, Gaza City',
              'The front of al-Shifa Medical Complex in Gaza City, February 2025.',
              'A heavily damaged hospital building with blackened windows, a bus and cars in front'),
    'salfit-wwtp': ('File:Salfit Wastewater Treatment Plant 01.jpg', '2024', 'Salfit wastewater plant',
                    'The Salfit wastewater treatment plant, February 2024: a working plant of the kind Kharas is waiting to start.',
                    'Grey buildings and tanks of a treatment plant inside a fence, olive terraces around'),
    'kifl-haris': ('File:مياه كفل حارس.jpg', '2024', 'Kifl Haris, Salfit',
                   'A Water Authority reservoir at Kifl Haris, Salfit governorate, April 2024.',
                   'A large round water tank behind a fence with a foundation plaque in front'),
    'asira': ('File:Water supply in West Bank and Gaza February 2014 9water photoblog.jpg', '2013', 'Asira al-Qibliya, Nablus',
              'A rooftop water tank in Asira al-Qibliya, Nablus governorate, a village on the grid without year-round supply. January 2013.',
              'A stone house with a black water container on its roof, power lines in front'),
    'tammun': ('File:Tammun8132.JPG', '2016', 'Tammun, Tubas',
               'Tammun, Tubas governorate, from the mountain, October 2016.',
               'Houses of Tammun spread along a dry valley floor'),
    'beita': ('File:Beita, Nablus 001.jpg', '2020', 'Beita, Nablus',
              'The entrance to Beita from the Huwwara road, with the village\'s overhead power line. June 2020.',
              'A field below houses on a hill, a wooden electricity pole with overhead lines in front'),
    'majaz': ('File:Al-Majaz village, Masafer Yatta 5.jpg', '2025', 'al-Majaz, Masafer Yatta',
              'Khirbet al-Majaz in Masafer Yatta, south of Hebron, the community the medical teams were trying to reach. 2025.',
              'Low structures, tents and animal pens on brown hillsides'),
    'athaba': ('File:05 05 2025 Khallet Athaba 01.jpg', '2025', 'Khallet Athaba, Masafer Yatta',
               'A demolition at Khallet Athaba, Masafer Yatta, 5 May 2025, when wells and water tanks were among the structures destroyed. Not al-Deirat.',
               'Excavators knocking down buildings while soldiers and military vehicles stand in front'),
    'beit-iksa': ('File:BeitIksaFeb172023 01.jpg', '2023', 'Beit Iksa, Jerusalem',
                  'Beit Iksa, north-west of Jerusalem, February 2023.',
                  'Houses of Beit Iksa on a hilltop above green terraces'),
    'qalandia': ('File:QalandiaVillageJan292023.jpg', '2023', 'Qalandia village',
                 'Qalandia village, in Jerusalem\'s suburbs, January 2023. The photo does not show the dump.',
                 'A wide view of Qalandia village\'s houses and the surrounding hills'),
    'salfit-hospital': ('File:Salfit Hospital 17.jpg', '2024', 'Yasser Arafat Hospital, Salfit',
                        'An ambulance outside Martyr Yasser Arafat Hospital, Salfit, April 2024.',
                        'A white ambulance marked in English and Arabic parked outside a hospital'),
    'pmrs': ('File:Palestinian Medical Relief Society, Salfit 2019.jpg', '2019', 'PMRS, Salfit',
             'The Palestinian Medical Relief Society centre in Salfit, which runs mobile clinics in Area C. January 2019.',
             'A stone building with a bilingual sign over its entrance'),
    'maleh': ('File:حمامات المالح في الأغوار الشمالية شرق طوباس فلسطين.jpg', '2025', 'Hammamat al-Maleh, Jordan Valley',
              'The old baths at Hammamat al-Maleh, among the springs of the northern Jordan Valley east of Tubas. Not al-Himma itself.',
              'Old stone ruins with arches, overgrown with grass and moss'),
    'najah': ('File:Najah 001.jpg', '2018', 'An-Najah University, Nablus',
              'An-Najah National University\'s new campus in Nablus, a partner in the AirAware network. No monitor is in the picture.',
              'The main entrance arch of a university campus with flags, blue sky'),
    'jericho-solar': ('File:Solar Plant in Jericho.jpg', '2014', 'Jericho solar plant',
                      'The photovoltaic plant at Jericho, October 2014.',
                      'Rows of solar panels on a flat desert plain, hills behind'),
    'rashash': ('File:פאנלים סולרים שבורים בעין רשאש 24-06-2023 1.jpg', '2023', 'Ein Rashash, Ramallah',
                'Solar panels smashed by settlers at Ein Rashash, Ramallah governorate, June 2023. Not Wadi al-A\'war.',
                'A small solar array with shattered glass on rocky ground at dusk'),
    'jordan-valley': ('File:Jordan Valley, West Bank 070 - Aug 2011.jpg', '2011', 'Jordan Valley',
                      'Eroded hills in the Jordan Valley, August 2011.',
                      'Bare pale hills under a blue sky with a dry plain in front'),
    'jenin-tanks': ('File:Roof water cistern in Jenin, West Bank 019 - Aug 2011.jpg', '2011', 'Jenin',
                    'Rooftop water tanks in Jenin, August 2011.',
                    'Black water tanks on a metal stand on a white house roof'),
}


# found after the research pass; metadata read from the Commons file page
P["File:Mas'udiya station.jpg"] = {'page_url': 'https://commons.wikimedia.org/wiki/File:Mas%27udiya_station.jpg', 'author': 'Haggibar',
                                    'license': 'CC0', 'license_url': 'https://creativecommons.org/publicdomain/zero/1.0/', 'date': '2002'}
PHOTO['masudiya'] = ("File:Mas'udiya station.jpg", '2002', 'al-Masoudiya, Nablus',
                     "The old railway station at al-Masoudiya, on Burqa's lands north-west of Nablus, in 2002.",
                     'A two-storey stone station building with arched doorways under a clear sky')


def photos():
    out = {}
    for slug, (f, year, place, cap, alt) in PHOTO.items():
        r = P[f]
        out[slug] = {'file': f, 'page_url': r['page_url'], 'author': r['author'], 'license': r['license'],
                     'license_url': r.get('license_url', ''), 'date': r.get('date', ''), 'year': year, 'place': place,
                     'caption': cap, 'alt': alt, 'credit': f"{r['author']}, {r['license']}"}
    out['qalandia']['pos'] = '40% 50%'
    return out


# ---------------------------------------------------------------- stations
def src(i):
    it = N[i]
    return it['source'].split(' (')[0].replace(', via OCHA', '') + ' via ' + it['via'].split(' (')[0].split(';')[0]


def station(code, short, place, subject, area, items, key=None, status=None, reading=None, what=None, word=False, photo=None, silent=None):
    key = key or items[-1]
    it = N[key]
    hist = sorted((N[i]['published'], N[i]['status']) for i in items)
    st = {'code': code, 'short': short, 'place': place, 'subject': subject, 'area': area,
          'status': status or it['status'], 'reading': reading or it['reading'], 'word': word,
          'what': what or it['reading_note'], 'source': src(key), 'date': it['published'], 'url': it['url'],
          'history': [list(h) for h in hist], 'item': key, 'items': list(items)}
    if photo:
        st['photo'] = photo
    if silent:
        st['status'] = 'silent'
        st['silent_since'] = silent
    return st


LINES = [
    {'key': 'water', 'name': 'Water', 'code': 'W', 'stations': [
        station('W1', 'Gaza output', 'Gaza Strip', 'Drinking-water production', 'gaza', ['gaza-water-production'],
                reading='−34%', what='drinking water produced 6–12 Oct against mid-September: two-thirds of the volume.', photo='kh-pumps'),
        station('W2', 'South desal', 'Deir al-Balah, Khan Younis', 'Seawater desalination plants', 'gaza', ['gaza-desal-south'],
                reading='74%', what='of Gaza\'s people rely on trucked drinking water; the two southern plants are at their lowest output.'),
        station('W3', 'Gaza chlorine', 'Gaza Strip', 'Water samples, chlorine', 'gaza', ['gaza-water-quality'], reading='>73%',
                what='of August\'s 938 samples were below the WHO chlorine level. No September figures since.', photo='wadi-gaza-2', silent='2026-09-28'),
        station('W4', 'Flood-risk sites', 'Gaza displacement sites', 'Flood risk before the rains', 'gaza', ['gaza-flood-sites'],
                what='people live in sites at medium to high risk of flooding; over 400,000 at high risk.', photo='wadi-gaza'),
        station('W5', 'Gaza wastewater', 'Gaza City, north Gaza', 'Wastewater and stormwater', 'gaza', ['sheikh-radwan-pool', 'gaza-north-wastewater'],
                what='people served by wastewater lines repaired in September; the Sheikh Radwan pump station was at 30% in mid-September.'),
        station('W6', 'Tubas lines', 'Tubas & Jordan Valley', 'Water lines and springs', 'wb-north',
                ['atouf-pipeline', 'himma-spring', 'tammun-loss', 'yarza-irrigation'], key='yarza-irrigation', reading='3 attacks',
                what='on water in 16 days: Atouf pipeline destroyed (29 Sep), concrete poured at al-Himma spring (7 Oct), meters stolen at Khirbet Yarza (14 Oct).',
                word=True, photo='maleh'),
        station('W7', 'Nablus networks', 'Nablus & Salfit villages', 'Village water networks', 'wb-north', ['beit-iba-well', 'lubban-loss'],
                reading='~50%', what='of the water put into al-Lubban ash-Sharqiya\'s network is lost before it reaches homes.', photo='kifl-haris'),
        station('W8', 'Hebron networks', 'Hebron governorate', 'Town networks and wastewater', 'wb-centre-south',
                ['deirat-well', 'kharas-wwtp', 'beit-ula-loss'], reading='~60%',
                what='of Beit Ula\'s water is lost in its network; the Kharas wastewater plant is still not running.', photo='salfit-wwtp'),
        station('W9', 'WB incidents', 'West Bank', 'Water and sanitation incidents', 'wb', ['wb-wash-incidents', 'wb-wash-networks'],
                key='wb-wash-incidents', status='watch', reading='24',
                what='incidents hit water and sanitation infrastructure in September; partners laid or repaired 32 km of network.', photo='jenin-tanks'),
    ]},
    {'key': 'air', 'name': 'Air & waste', 'code': 'A', 'stations': [
        station('A1', 'Gaza waste', 'Gaza City', 'Solid waste dumps', 'gaza', ['gaza-feras-dump'], word=True,
                what='the Feras Market temporary dump was cleared in September; collection still relies on donkey carts and UN trucks.'),
        station('A2', 'Nablus air', 'Nablus', 'AirAware air sensors', 'wb-north', ['airaware-nablus'], reading='5',
                what='air-quality stations launched with a public data platform. No reading or update has been published since.',
                photo='najah', silent='2026-09-16'),
        station('A3', 'Illegal dumps', 'Qalandia, Jerusalem', 'Illegal waste dumps', 'jerusalem', ['qalandia-dump'], word=True,
                what='the entrance to a dump used for smuggled waste was blocked with three barriers.', photo='qalandia'),
        station('A4', 'Landfills', 'West Bank', 'Landfills and climate plan', 'wb', ['wb-solid-waste-wb', 'ndc3'],
                what='costed measures in Palestine\'s third climate plan, launched 19 Oct; a $25m landfill programme was reviewed on 15 Oct.',
                photo='jordan-valley'),
    ]},
    {'key': 'power', 'name': 'Power', 'code': 'P', 'stations': [
        station('P1', 'Desal power', 'Southern Gaza', 'Desalination plant power', 'gaza', ['gaza-desal-power'], word=True),
        station('P2', 'Clinic fuel', 'Gaza health facilities', 'Fuel, engine oil, spares', 'gaza', ['gaza-fuel-oil-health'], word=True,
                what='fuel, engine oil and generator parts are short; dialysis and cancer care are at risk.'),
        station('P3', 'Cooking gas', 'al-Mawasi, Khan Younis', 'Cooking gas', 'gaza', ['gaza-cooking-gas'],
                what='a kilo of cooking gas on the black market, against 75 shekels for an 8 kg cylinder from the distributor.', photo='mawasi'),
        station('P4', 'Nablus lines', 'Beita & Burqa, Nablus', 'Village power lines', 'wb-north', ['masoudiya-power', 'beita-power'],
                key='beita-power', reading='Day 3', word=True,
                what='a Beita family without power after settler cuts; al-Masoudiya was cut for the fifth time on 12 Oct.', photo='beita'),
        station('P5', 'Wadi al-A\'war', 'Wadi al-A\'war, Hebron', 'Village power lines', 'wb-centre-south', ['wadi-awar-power'],
                what='homes cut off when settlers severed the lines, the sixth time in a row.', photo='rashash'),
        station('P6', 'Solar pumping', 'Nablus governorate', 'Solar plant for water pumps', 'wb-north', ['nablus-solar-water'],
                what='of land handed to the Water Authority for a solar plant to power its pumping stations.', photo='jericho-solar'),
    ]},
    {'key': 'health', 'name': 'Health', 'code': 'H', 'stations': [
        station('H1', 'Gaza disease', 'Gaza Strip', 'Communicable disease', 'gaza', ['gaza-who-winter', 'gaza-communicable'],
                what='of consultations, 4–10 Oct, were for communicable disease; WHO warns of winter outbreaks.'),
        station('H2', 'Gaza medicines', 'Gaza Strip', 'Essential medicines', 'gaza', ['gaza-labs', 'gaza-meds-zero'], key='gaza-meds-zero',
                what='of essential medicines at zero stock; half the laboratory equipment is destroyed.', photo='shifa'),
        station('H3', 'Gaza hospitals', 'Gaza Strip', 'Hospitals working', 'gaza', ['gaza-hospitals-functional'],
                what='hospitals and field hospitals partly working, 1 Jan–30 Sep; WHO counts 88 attacks on health care.'),
        station('H4', 'Gaza polio', 'Gaza Strip', 'Polio (AFP) surveillance', 'gaza', ['gaza-afp'], reading='22',
                what='acute flaccid paralysis cases this year, to 20 Sept. No surveillance update since.', silent='2026-09-28'),
        station('H5', 'Masafer teams', 'Masafer Yatta, Area C', 'Mobile medical teams', 'area-c', ['area-c-mobile-clinics', 'masafer-medical'],
                key='masafer-medical', word=True, what='settlers stopped medical teams on the way to Khirbet al-Majaz; 17 Area C locations have no mobile clinic.',
                photo='majaz'),
        station('H6', 'WB attacks', 'West Bank', 'Attacks on health care', 'wb', ['wb-health-attacks'],
                what='attacks on health care recorded by WHO, January to September.', photo='salfit-hospital'),
    ]},
]

P_ = lambda i: N[i]

EDITION = {
    'date': '2026-10-20', 'weekday': 'Tuesday', 'sweep': '07:00', 'window': ['2026-09-21', '2026-10-20'],
    'description': 'Canary Palestine listens to water, air, power and health in Gaza and the West Bank, station by station, and says early when something goes quiet.',
    'about': 'Canary Palestine is an early-warning newsroom for water, air, power and health in Gaza and the West Bank. It listens to named reports, station by station, and says so when a station goes quiet.',
    'lead': {
        'codes': ['W1', 'P1'], 'status': 'alert', 'when': 'OCHA report, 19 Oct', 'photo': 'kh-pumps', 'id': 'gaza-water-production',
        'headline': 'Gaza is making a third less drinking water than in mid-September',
        'dek': 'Repairs cut the line to northern Gaza for most of eight days, the Bani Suheila line was down for two, and the southern desalination plant lost power. Eleven water partners may stop work.',
        'reading_note': 'drinking water produced 6–12 Oct, against the weekly volume in mid-September',
        'src': 'OCHA humanitarian situation report of 15 Oct (published 19 Oct), WASH Cluster data',
    },
    'newest': [
        {'id': 'beita-power', 'date': '2026-10-20', 'code': 'P4', 'text': 'Beita family without power for a third day', 'photo': 'beita'},
        {'id': 'ndc3', 'date': '2026-10-19', 'code': 'A4', 'text': 'Third climate plan sets out 175 costed measures', 'photo': 'jordan-valley'},
        {'id': 'gaza-flood-sites', 'date': '2026-10-19', 'code': 'W4', 'text': '950,000 people in flood-risk sites before the rains', 'photo': 'wadi-gaza'},
        {'id': 'beit-ula-loss', 'date': '2026-10-18', 'code': 'W8', 'text': 'Beit Ula loses about 60% of its water', 'photo': 'salfit-wwtp'},
        {'id': 'masafer-medical', 'date': '2026-10-15', 'code': 'H5', 'text': 'Medical teams stopped on the way to al-Majaz', 'photo': 'majaz'},
    ],
    'silence': {'title': 'Silence is the signal.',
                'say': 'A canary that stops singing is the warning. When a station has had no public report for weeks, the desk does not fill the gap; it counts the days and asks why.'},
    'feature': {'s': 'alert', 'codes': 'P4 · al-Masoudiya', 'kicker': 'Power · Nablus · 12 Oct', 'photo': 'masudiya', 'id': 'masoudiya-power',
                'headline': 'Five times in two months, settlers have cut al-Masoudiya\'s power',
                'body': P_('masoudiya-power')['body'].split('\n\n') if isinstance(P_('masoudiya-power')['body'], str) else P_('masoudiya-power')['body']},
    'cards': [
        {'id': 'meds', 'rid': 'gaza-meds-zero', 's': 'alert', 'codes': 'H2', 'kicker': 'Health · Gaza', 'photo': 'shifa', 'url': P_('gaza-meds-zero')['url'],
         'headline': 'Gaza hospitals have none of 44% of their essential medicines', 'summary': P_('gaza-meds-zero')['summary'].split('. Imaging')[0] + '.',
         'src': src('gaza-meds-zero') + ' · 8 Oct'},
        {'id': 'flood', 'rid': 'gaza-flood-sites', 's': 'alert', 'codes': 'W4', 'kicker': 'Water · Gaza', 'photo': 'mawasi', 'url': P_('gaza-flood-sites')['url'],
         'headline': 'Before the rains, 950,000 displaced people live where floods reach', 'summary': P_('gaza-flood-sites')['summary'].split(' IOM')[0],
         'src': src('gaza-flood-sites') + ' · 19 Oct'},
        {'id': 'himma', 'rid': 'himma-spring', 's': 'alert', 'codes': 'W6', 'kicker': 'Water · Jordan Valley', 'photo': 'maleh', 'url': P_('himma-spring')['url'],
         'headline': 'Settlers pour concrete at al-Himma spring', 'summary': P_('himma-spring')['summary'],
         'src': src('himma-spring') + ' · 7 Oct'},
        {'id': 'attacks', 'rid': 'wb-health-attacks', 's': 'watch', 'codes': 'H6', 'kicker': 'Health · West Bank', 'photo': 'salfit-hospital', 'url': P_('wb-health-attacks')['url'],
         'headline': '146 attacks on West Bank health care this year',
         'points': [['146', 'attacks recorded by WHO, 1 Jan–30 Sep'], ['113', 'health transports affected'], ['25', 'health facilities affected'],
                    ['131', 'cases of care being obstructed']],
         'src': src('wb-health-attacks') + ' · 16 Oct'},
    ],
    'more': [
        {'id': i, 's': N[i]['status'], 'codes': c, 'date': N[i]['published'], 'photo': ph, 'url': N[i]['url'], 'headline': N[i]['headline'],
         'src': src(i)}
        for i, c, ph in [('tammun-loss', 'W6', 'tammun'), ('kharas-wwtp', 'W8', 'salfit-wwtp'), ('beit-iksa-sewage', 'W', 'beit-iksa'),
                         ('deirat-well', 'W8', 'athaba'), ('wb-wash-networks', 'W9', 'asira'), ('area-c-mobile-clinics', 'H5', 'pmrs')]
    ],
    'lines': LINES,
}


# ---------------------------------------------------------------- report pages
# Every sourced item gets a page. Its photo is the one the research matched to it (suggested_for, then
# also_fits), only if that photo is in the set above; otherwise the page carries its station's call.
FILE2SLUG = {f: slug for slug, (f, *_rest) in PHOTO.items()}
RESEARCH_PHOTOS = json.load(open(os.path.join(ROOT, 'research', 'photos.json'), encoding='utf-8'))


def report_photo(i):
    for r in RESEARCH_PHOTOS:
        if r['suggested_for'] == i and r['file'] in FILE2SLUG:
            return FILE2SLUG[r['file']]
    for r in RESEARCH_PHOTOS:
        if i in (r.get('also_fits') or []) and r['file'] in FILE2SLUG:
            return FILE2SLUG[r['file']]
    return None


STATION_OF = {i: st['code'] for l in LINES for st in l['stations'] for i in st['items']}
EXTRA_PHOTO = {'masoudiya-power': 'masudiya', 'gaza-water-production': 'kh-pumps'}
KEEP = ('id', 'date', 'published', 'line', 'area', 'place', 'subject', 'status', 'reading', 'reading_note', 'headline', 'summary',
        'source', 'via', 'url', 'background')
EDITION['reports'] = []
for i, it in N.items():
    if it.get('confidence') != 'verified':
        continue
    body = it.get('body') or ''
    r = {k: it[k] for k in KEEP}
    r['body'] = [b for b in body.split(chr(10) * 2) if b.strip()] if isinstance(body, str) else body
    r['station'] = STATION_OF.get(i)
    r['photo'] = EXTRA_PHOTO.get(i) or report_photo(i)
    r['src'] = src(i)
    EDITION['reports'].append(r)
EDITION['reports'].sort(key=lambda r: (r['published'], r['date']), reverse=True)

if __name__ == '__main__':
    json.dump(EDITION, open(os.path.join(ROOT, 'tools', 'edition.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(photos(), open(os.path.join(ROOT, 'tools', 'photos.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    n = sum(len(l['stations']) for l in LINES)
    print('stations', n, 'with photo', sum(1 for l in LINES for s in l['stations'] if s.get('photo')))
    rs = EDITION['reports']
    print('reports', len(rs), 'with photo', sum(1 for r in rs if r['photo']), 'no station', [r['id'] for r in rs if not r['station']])
