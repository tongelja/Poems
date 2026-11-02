# Poems

Poems and quotations kept in [poems.adoc](poems.adoc), with a small web site
that shows a random one.

    make serve        # run locally at http://127.0.0.1:5056

Pages: `/` random entry (`?kind=poem` or `?kind=quote`), `/all` the full list,
`/p/<slug>` one entry, `/api/random` and `/api/entries` as JSON.

## Adding and editing poems

Edit poems.adoc on GitHub (or locally, then push). The Pi pulls from GitHub
every 5 minutes, and the site re-reads poems.adoc when it changes, so edits
show up on their own.

## Checking poems.adoc

`make check` lists any broken blocks or headings by line number. The same check runs:

- before each local commit that touches poems.adoc (run `make hooks` once to turn it on)
- on GitHub after every push, including edits made in the web editor (a failed check emails you)
- on the Pi before it pulls, so a broken version never reaches the site

## Azure

Every push to master also builds a static copy of the site (`web/build_static.py`)
and publishes it to Azure Static Web Apps (`.github/workflows/azure-static-web-app.yml`).
The build stops if poems.adoc has problems, so the last good version stays up.
On the static site the random pick on `/` happens in the browser.

    cd web && uv run python build_static.py     # build into dist/ to look at locally

## The Pi (http://192.168.3.95:5056)

The Pi keeps a git checkout in `~/Poems`. `deploy/pull.sh` runs every 5
minutes (`poems-pull.timer`); if anything other than poems.adoc changed, it
also syncs dependencies and restarts the site.

    make deploy       # first-time setup, or apply a pushed change right away
