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

## The Pi (http://192.168.3.95:5056)

The Pi keeps a git checkout in `~/Poems`. `deploy/pull.sh` runs every 5
minutes (`poems-pull.timer`); if anything other than poems.adoc changed, it
also syncs dependencies and restarts the site.

    make deploy       # first-time setup, or apply a pushed change right away
