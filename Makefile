poems:
	asciidoctor-pdf poems.adoc &&  mv poems.pdf poems-`date '+%Y%m%d'`.pdf
clean:
	rm *.pdf
