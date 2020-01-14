
# Language in ['en', 'fr', 'pl', 'es', 'tr', 'ch']
LANGUAGE = fr

# Arguman url
ARGUMAN = https://$(LANGUAGE).arguman.org

# Directories
SRC = $(LANGUAGE)/src
CSV = $(LANGUAGE)/csv
XML = $(LANGUAGE)/xml


# Csv storing page's urls
CSV_PAGES = $(CSV)/all_pages.csv

# Gather page ids from the csv
PAGE_IDS = $(shell if test -f $(CSV_PAGES); then cat $(CSV_PAGES) | cut -d ';' -f 1; else echo ""; fi)



# Generate XML from all known page ids
all: download $(foreach pid, $(PAGE_IDS), $(XML)/page_$(pid).xml)

# Download all pages (read page_ids in CSV_PAGES)
download: $(foreach pid, $(PAGE_IDS), $(SRC)/pages/$(pid).html)
	@-test "$^" || echo "Please use 'make download_all_page' first"

# Download all page's urls from Arguman's front page
download_all_pages: $(CSV_PAGES)



# ###
# Fetching debate's urls from the Arguman's front page
# ###

# Download the front page
$(LANGUAGE)/src/pages/all_pages.html: | $(SRC)/pages/
	wget -q $(ARGUMAN) -O $@

# Extract urls from the front page
$(CSV_PAGES): $(SRC)/pages/all_pages.html | $(CSV)/
	cat $< | grep 'h3' | sed 's/^.*href="\([^>]*\)".*$$/\1/' | awk '{num += 1; print num ";" $$0}' > $@





# ###
# Fetching a debate page
# ###

# Download a page given its page_id
$(SRC)/pages/%.html: $(CSV_PAGES) | $(SRC)/pages/
	$(eval url := $(shell cat $< | grep '^$*;' | cut -d ';' -f 2))
	./download_page.sh $(ARGUMAN)/$(url) $@

# Correct html tags
$(SRC)/valid/%.html: $(SRC)/pages/%.html | $(SRC)/valid/
	cat $< | grep -v '\(<meta.*>\|<input.*>\|<br.*>\|<img.*>\)' | sed 's/&/ /g' > $@

# Execute a xslt stylesheet on a given page
$(XML)/page_%.xml: debate2xml.xsl $(SRC)/valid/%.html | $(XML)/
	xsltproc $^ > $@









# Make directories
$(SRC)/pages/ $(SRC)/valid/ $(XML)/ $(CSV)/:
	mkdir -p $@


# Clean
clean:
	rm -fr $(SRC)/ $(CSV)/ $(XML)/


# Not a file (always an active recipe)
.PHONY: all download download_all_pages clean
