# Poems

Poems and quotations kept in [poems.adoc](poems.adoc), with a small web site
that shows a random one.

    make serve        # http://127.0.0.1:5056
    make deploy       # copy to the Pi and restart (port 5056)

Pages: `/` random entry (`?kind=poem` or `?kind=quote`), `/all` the full list,
`/p/<slug>` one entry, `/api/random` and `/api/entries` as JSON.

The site re-reads poems.adoc whenever it changes, so new poems show up without a restart.
