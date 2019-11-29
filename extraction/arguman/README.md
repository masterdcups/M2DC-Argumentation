
# Extraction from Argüman

*Version 0.1.ß*

### Use

We use a Makefile to manage the extraction

	# Download page urls from Argüman front page
	# It generates fr/csv/all_pages.csv
	make download_all_pages

	# Download all pages from urls found in this csv
	# It generates fr/src/pages/i.html
	make download
	
	# Generate XML using XSLT stylesheet for pages (and download it before, if necessary)
	# It generates fr/xml/page_i.xml
	make
	
We can edit the Makefile or add LANGUAGE=xx to any command to extract pages of any language. We can use (fr|en|tr|es|ch|pl)

*Note:* We scrap the html since there is no API. There are blocks of missing data that are normally fetched in javascript. We use the script *download_page.sh* to recursively download data and paste it directly in the source code.

### Format

Actually we extract a debate using this format:

	<?xml version="1.0"?>
	<debate>
	  <debate-title>...</debate-title>
	  <debate-url>...</debate-url>
	  <debate-author>...</debate-author>
	  <premises>
	    <premise>
	      <premise-id>...</premise-id>
	      <premise-ref>...</premise-ref>
	      <premise-type>...</premise-type>
	      <premise-weight>...</premise-weight>
	      <premise-content>...</premise-content>
	      <premise-author>...</premise-author>
	      <premise-date>...</premise-date>
	      <premise-support>...</premise-support>
	      <premise-fallacies>
	        <fallacy>
	          <fallacy-type>...</fallacy-type>
	          <fallacy-reason>...</fallacy-reason>
	        </fallacy>
	      </premise-fallacies>
	    </premise>
	    <premise>...</premise>
	  </premises>
	</debate>

We can build the argument graph using premise-ids and premise-refs. Premise-types are (because|but|however) as in Argüman semantics.

It's obviously temporary notations. Furthermore, there are many useless features.

It may be easier to open a XML file and to look at its structure. For instance, have a look to [this file](fr/xml/page_1.xml)

