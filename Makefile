poems:
	git add poems.adoc
	git commit -m "Add $( date '+%Y%m%d ) poems"
	git push
	asciidoctor-pdf poems.adoc &&  mv poems.pdf poems-`date '+%Y%m%d'`.pdf
clean:
	rm *.pdf
