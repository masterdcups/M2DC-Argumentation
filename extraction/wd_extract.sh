#! /bin/sh

# Extract the argumentation graph of WikiDebats
# Usage: extract_wd.sh (no arguments)


# Parse command-line arguments
usage() {
    echo "$0: usage: (no arguments)" >&2
}
test $# -ne 0 && usage && exit 1


# Globals
WD_URL="https://wikidebats.org/wiki"
WD_SITEMAP="$WD_URL/Cat%C3%A9gorie:D%C3%A9bats"
OUTPUT_DIR="wd"


# Create CSVs' output directory
mkdir -p $OUTPUT_DIR


# Download and convert the sitemap
echo "Extract sitemap: $WD_SITEMAP"
wget -q $WD_SITEMAP -O - \
    | xsltproc xslt/wd_sitemap.xsl - \
    | sed 's/.wiki.//' > $OUTPUT_DIR/sitemap.csv


# Download and convert all pages (iterate until no new page is downloaded)
n_files1=0
n_files2=`ls $OUTPUT_DIR/*.csv | wc -w`
while test $n_files1 -ne $n_files2
do 
    urls=`cat $OUTPUT_DIR/*.csv | cut -d ';' -f 1`
    for url in $urls
    do 
	if test ! -f $OUTPUT_DIR/$url.csv
	then
	    echo "Extract page: $url"
	    wget -q "$WD_URL/$url" -O - \
		| xsltproc xslt/wd_page.xsl - \
		| sed 's/.wiki.//' \
		| tr '/' '~' > "$OUTPUT_DIR/`echo "$url" | tr '/' '~'`.csv"
	fi
    done
    n_files1=$n_files2
    n_files2=`ls $OUTPUT_DIR/*.csv | wc -w`
done

# Build the wd_nodes.csv and wd_edges.csv graph representation
echo "Create '${OUTPUT_DIR}_nodes.csv' and '${OUTPUT_DIR}_edges.csv'"
python3 mk_graph.py $OUTPUT_DIR







