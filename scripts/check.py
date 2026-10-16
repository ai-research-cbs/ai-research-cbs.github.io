"""Check the locked navigation and the generated static site. Run after Jekyll."""
import json
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def rows(name):
    return [json.loads(line[2:]) for line in (ROOT / '_data' / name).read_text().splitlines() if line.startswith('- ')]


EXPECTED = [
    ('Home', 'home', []),
    ('AI as a Tool', 'tool', ['Ideation', 'Writing', 'Background', 'Coding', 'Analysis', 'Math']),
    ('AI as a Topic', 'topic', ['Information Extraction', 'Economic Implications', 'Modeling Complex Relationships', 'Benchmarking Human Decisions', 'Intellectual Transfer']),
    ('AI as a Substitute', 'substitute', ['Narrative', 'Exposure', 'What Should We Do?']),
    ('Infrastructure', 'infrastructure', ['Data', 'Code', 'Taste']),
]


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids, self.links, self.assets = set(), [], []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            assert attrs['id'] not in self.ids, f'Duplicate ID: {attrs["id"]}'
            self.ids.add(attrs['id'])
        if tag == 'a' and 'href' in attrs:
            self.links.append(attrs['href'])
        if tag in ('img', 'script') and 'src' in attrs:
            self.assets.append(attrs['src'])
        if tag == 'link' and attrs.get('rel') in ('stylesheet', 'icon'):
            self.assets.append(attrs['href'])


def check():
    sections = rows('sections.yml')
    actual = [(s['title'], s['slug'], [p['title'] for p in s['pages']]) for s in sections]
    assert actual == EXPECTED, actual
    expected_paths = ['/']
    for section in sections[1:]:
        expected_paths.append(section['url'])
        for page in section['pages']:
            expected_paths.append(f'/{section["slug"]}/{page["slug"]}/')
    docs = {}
    for path in expected_paths:
        file = ROOT / '_site' / path.lstrip('/') / 'index.html'
        assert file.is_file(), f'Missing page: {path}'
        text = file.read_text()
        assert '{{' not in text and '{%' not in text, f'Unrendered template: {path}'
        docs[path] = Document(text)
    for path, doc in docs.items():
        for href in doc.links + doc.assets:
            url = urlsplit(href)
            if url.scheme or url.netloc:
                continue
            target = unquote(url.path) or path
            if target.endswith('/'):
                assert target in docs, f'{path}: missing target {href}'
                if url.fragment:
                    assert unquote(url.fragment) in docs[target].ids, f'{path}: missing anchor {href}'
            else:
                assert (ROOT / '_site' / target.lstrip('/')).is_file(), f'Missing asset {href}'
    readings = rows('readings.yml')
    assert len(readings) == 65
    assert len({(r['section'], r['page'], r['title']) for r in readings}) == len(readings)
    for r in readings:
        assert all(r.get(k) for k in ('section', 'page', 'title', 'author', 'year', 'length', 'kind')), r
        assert type(r['year']) is int, r
        assert f'/{r["section"]}/{r["page"]}/' in docs, r
        assert 'level' not in r
        if r['url']:
            assert r['url'].startswith('https://'), r
    groups = Counter(r['group'] for r in readings if r.get('group'))
    assert groups == {'Macro Implications': 6, 'Labor Markets': 21, 'Financial Sector': 10, 'Alignment and Governance': 3}, groups
    assert len([r for r in readings if not r['url']]) == 3
    print(f'PASS: five ordered tabs, 17 ordered subsections, {len(docs)} built routes, all local links and assets, 65 readings, 40 grouped papers.')


if __name__ == '__main__':
    check()
