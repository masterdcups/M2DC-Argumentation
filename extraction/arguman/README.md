
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

*Note:* We scrap the html since there is no API. There are blocks of missing data that are normally fetched in javascript. We use the script *download_page.sh* to recursively download data and paste it directly in the downloaded html.

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
	      <premise-sources>
	        <source>...</source>
	        <source>...</source>
	        ...
	      </premise-sources>
	      <premise-support>...</premise-support>
	      <premise-fallacies>
	        <fallacy>
	          <fallacy-type>...</fallacy-type>
	          <fallacy-reason>...</fallacy-reason>
	        </fallacy>
	        <fallacy>...</fallacy>
	        ...
	      </premise-fallacies>
	    </premise>
	    <premise>...</premise>
	    <premise>...</premise>
	    <premise>...</premise>
	    ...
	  </premises>
	</debate>

We can build the argument graph using premise-ids and premise-refs. Premise-types are (because|but|however) as in Argüman semantics.

It's obviously temporary notations. Furthermore, there are many useless features.

It may be easier to open a XML file and to look at its structure. For instance, have a look to [this file](fr/xml/page_1.xml) (you may want to open it with your web browser to enjoy indentation)


### Script description

Basically we use xslt to parse a debate page. Let explain it more in details:

1. We fetch all the debate page urls we can find on the front page to build a csv. The *Makefile* just greps *h3* lines, extract *a*'s *href* attributes, and write them with a numerical id.
2. We download a page given its numerical id. The *Makefile* asks the script *download_page.sh* to recursively download page and dynamic data blocks.
3. We simply clean the html using *sed* command in the *Makefile*.
4. We transform the html into the given xml format, using the *debate2xml.xsl* XSLT stylesheet.
