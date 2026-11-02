"""Render the Poems site as static files (for Azure Static Web Apps) into ../dist.

    uv run python build_static.py [--out DIR]
"""
import argparse
import json
import os
import shutil
from pathlib import Path

os.environ['POEMS_STATIC'] = '1'

import poemsApp  # noqa: E402

HERE = Path(__file__).parent

AZURE_CONFIG = {
    'trailingSlash': 'auto',
    'responseOverrides': {'404': {'rewrite': '/404.html'}},
    'mimeTypes': {'.json': 'application/json'},
    'routes': [
        {'route': '/static/*', 'headers': {'Cache-Control': 'public, max-age=86400'}},
    ],
}


def write(out, url, body):
    path = out / url.lstrip('/')
    if url.endswith('/'):
        path = path / 'index.html'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default=str(HERE.parent / 'dist'))
    out = Path(parser.parse_args().out)

    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(HERE / 'static', out / 'static')
    (out / 'staticwebapp.config.json').write_text(json.dumps(AZURE_CONFIG, indent=2))

    client = poemsApp.app.test_client()
    pages = ['/', '/all/', '/404.html', '/api/entries.json']
    pages += ['/p/{}/'.format(e.slug) for e in poemsApp.LIBRARY.entries]
    for url in pages:
        response = client.get(url)
        expected = 404 if url == '/404.html' else 200
        if response.status_code != expected:
            raise SystemExit(f'{url} returned {response.status_code}')
        write(out, url, response.data)

    size = sum(f.stat().st_size for f in out.rglob('*') if f.is_file())
    print(f'Built {len(pages)} files ({size / 1e6:.1f} MB) into {out}')


if __name__ == '__main__':
    main()
