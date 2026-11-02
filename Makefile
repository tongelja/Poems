poems:
	git add poems.adoc
	git commit -m "Add $( date '+%Y%m%d' ) poems"
	git push
	asciidoctor-pdf poems.adoc &&  mv poems.pdf Poems.pdf
serve:
	cd web && uv run flask --app poemsApp run --debug --port 5056
deploy:
	deploy/deploy.sh
clean:
	rm *.pdf
