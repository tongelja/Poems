import random
from pathlib import Path

from flask import Flask, abort, jsonify, redirect, render_template, request, url_for

from adoc import Library

app = Flask(__name__)

LIBRARY = Library(Path(__file__).parent.parent / 'poems.adoc')
KINDS = {'poem': 'Poems', 'quote': 'Quotes'}


def pick(kind=None, exclude=None):
    pool = [e for e in LIBRARY.entries if (not kind or e.kind == kind) and e.slug != exclude]
    return random.choice(pool or LIBRARY.entries)


def chosen_kind():
    kind = request.args.get('kind')
    return kind if kind in KINDS else None


@app.context_processor
def globals_():
    return {'kinds': KINDS, 'kind': chosen_kind()}


@app.route('/')
def home():
    """A random poem or quote. Refresh for another."""
    entry = pick(chosen_kind(), exclude=request.args.get('after'))
    return render_template('entry.html', entry=entry, random_view=True)


@app.route('/random')
def random_entry():
    return redirect(url_for('entry', slug=pick(chosen_kind()).slug))


@app.route('/p/<slug>')
def entry(slug):
    e = LIBRARY.get(slug) or abort(404)
    entries = LIBRARY.entries
    i = entries.index(e)
    return render_template('entry.html', entry=e, random_view=False,
                           prev=entries[i - 1], next=entries[(i + 1) % len(entries)])


@app.route('/all')
def index():
    return render_template('index.html', sections=LIBRARY.sections(), total=len(LIBRARY.entries))


@app.route('/api/random')
def api_random():
    return jsonify(pick(chosen_kind()).as_dict())


@app.route('/api/entries')
def api_entries():
    return jsonify([e.as_dict() for e in LIBRARY.entries])


@app.errorhandler(404)
def not_found(_):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
