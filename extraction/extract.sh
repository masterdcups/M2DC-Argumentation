#! /bin/bash

#
# Extract the argument graph of:
#  - WikiDebats [fr]
#  - Tialo [en]
#  - Argüman [fr|en|es|pl|tr]
#
#
# usage: extract.sh [ wikidebats | tialo | arguman [fr|en|es|pl|tr|ch] ] [ --n_threads n ] [ --clean ]
#




# Globals

LANGUAGE=fr

WD_ID="wd"
WD_URL="https://wikidebats.org/wiki"
WD_SITEMAP="$WD_URL/Cat%C3%A9gorie:D%C3%A9bats"

AM_ID="am"
AM_URL="https://$LANGUAGE.arguman.org"
AM_SITEMAP="$AM_URL"

KL_ID="kl"
KL_URL="https://www.kialo.com"
KL_SITEMAP="$KL_URL"

N_THREADS=1
CLEAN=""



# Parse command-line arguments
usage() { # $1=msg
    echo "$0: usage: $0 website [language] [--n_threads n] [--clean]" >&2
    test "$1" && echo "$0: $1" >&2
}
if test $# -eq 0
then
    usage
    exit 1
fi
case "$1" in
    wd | wikidebats)
	SITE=$WD_ID
	URL=$WD_URL
	SITEMAP=$WD_SITEMAP
	LANGUAGE=""
	OUTPUT_DIR=$WD_ID
	;;
    am | arguman)
	SITE=$AM_ID
	LANGUAGE="fr"
	URL=$AM_URL
	SITEMAP=$AM_SITEMAP
	OUTPUT_DIR=$AM_ID-$LANGUAGE
	echo $SITEMAP
	;;
    kl | kialo)
	SITE=$KL_ID
	URL=$KL_URL
	SITEMAP=$KL_SITEMAP
	OUTPUT_DIR=$KL_ID
	;;
    *)
	usage "website argument must be in { wd, wikidebats, am, arguman, kl, kialo }"
	exit 2
	;;
esac
shift

while test $# -gt 0
do
    case "$1" in
	fr | en | es | pl | tr | ch )
	    if test ! $SITE = $AM_ID
	    then
		usage "language selection is available for argüman only"
		exit 3
	    fi
	    LANGUAGE=$1
	    URL="https://$LANGUAGE.arguman.org"
	    SITEMAP=$URL
	    OUTPUT_DIR=$AM_ID-$LANGUAGE
	    shift
	    ;;
	--n_threads)
	    shift
	    expr "$1" + 1 > /dev/null 2>&1
	    test $? -ne 0 && usage "n must be a positive integer" && exit 4
	    N_THREADS=$1
	    shift
	    ;;
	--clean)
	    CLEAN="yes"
	    shift
	    ;;
	*)
	    usage
	    exit 5
	    ;;
    esac
done



# Create CSVs' output directory
mkdir -p $OUTPUT_DIR


# Extraction functions

# Extraction from WikiDebats
wd_extract_sitemap() {
    echo "#domain: $1"
    echo "#url: $2"
    cat \
	| xsltproc xslt/wd_sitemap.xsl - \
	| sed 's/.wiki.//'
}
wd_extract_page() {
    echo "#domain: $1"
    echo "#url: $2"
    cat \
	| tr '\n' ' ' \
	| xsltproc xslt/wd_page.xsl - \
	| sed 's/.wiki.//' \
	| grep -v '\[ Modifier \]' 
}
wd_extract_subpage() {
    cat \
	| wd_extract_page
}


# Extraction from Argüman
am_extract_sitemap() {
    echo "#domain: $1"
    echo "#url: $2"
    echo "#name: sitemap"
    echo "#description: argüman [$LANGUAGE]"
    cat \
	| grep '<h3>' \
	| sed 's/^.*href=".\(.*\)">\(.*\)<.a>.*$/\1;\2;0/' \
	| tr '"' "'" 
}
am_extract_page() { # $1=url
    echo "#domain: $1"
    echo "#url: $2"
    cat \
	| tr -d '\n'  \
	| sed 's/&/&amp;/g' \
	| sed 's/.permalink/permalink/g' \
	| sed 's/^.*\(<div id="app".*\)<div id="list-view-indicator" class="tooltip">.*$/\1/' \
	| xsltproc xslt/am_page.xsl - \
	| sed "s/--place-url-here--/$2/" \
	| tr '"' "'"
}
am_extract_subpage() {
    echo "#domain: $1"
    echo "#url: $2"
    base_url="`echo "$2" | sed 's/?.*$//'`"
    cat \
	| tr -d '\n' \
	| xsltproc xslt/am_subpage.xsl - \
	| sed "s/--place-url-here--/$base_url/" \
	| tr '"' "'"
}

# Extraction from Kialo
kl_extract_sitemap() {
    echo "#domain: $1"
    echo "#url: $2"
    cat \
	| grep -v '\(<svg\|<use\|<img\)' \
	| sed "s/https:..www.kialo.com.//" \
	| tr '\n' '\f' \
	| sed 's/^.*\(<main.*main>\).*$/\1/' \
	| sed 's/\( \|\t\|\r\|\f\)\+/ /g' \
	| xsltproc xslt/kl_sitemap.xsl - \
	| sed 's/.path=[^;]*;/;/' \
	| sed 's/ *; */;/g' 
}
kl_extract_page() {
    echo "#domain: $1"
    echo "#url: $2"
    cat \
	| sed 's/https:..www.kialo.com.//' \
	| sed 's/xlink:[^ ]*="[^"]*"//g' \
	| sed 's/tabindex="0" disabled role="button"//' \
	| sed 's/&..\?.\?.\?;//g' \
	| tr '\n' '\f' \
	| sed 's/^.*\(<main.*main>\).*$/\1/' \
	| tr '\f' ' ' \
	| xsltproc xslt/kl_page.xsl - \
	| sed 's/.path=[^;]*;/;/' \
	| sed 's/ *; */;/g'
}
kl_extract_subpage() {
    cat \
	| kl_extract_page
}



# Index function
INDEX="$OUTPUT_DIR/index.txt"
declare -A nums
if test -f $INDEX 
then
    echo "Read index"
    while read line
    do
	arr=(${line//;/ }) #arr[0]=url; arr[1]=num
	if test "${arr[0]}"
	then
	    nums["${arr[0]}"]=${arr[1]}
	fi
    done < $INDEX
else
    echo "Create new index: $INDEX"
    echo -n "" > $INDEX
fi

num_of() { # $1=value; 'return'  the number
    if test ! "${nums["$1"]}"
    then
	value="`echo "$1" | sed 's/\(\*\)/./g'`"
	grep '^'"$value"';' $INDEX > /dev/null 2>&1
	if test $? -eq 0
	then
	    num="`grep '^'"$value"';' $INDEX | cut -d ';' -f 2`"
	else
	    num=`cat $INDEX | wc -l`
	    echo "$1;$num" >> $INDEX

	fi
	nums[$1]=$num
    fi
    echo "${nums[$1]}"
}




# Delete incomplete files if any (files of only one line)
if test "$CLEAN"
then
    echo -n "Check for incomplete files... "
    fs=`wc -l $OUTPUT_DIR/*.csv | tr -s ' ' | sed 's/^ //' | grep '^1 ' | cut -d ' ' -f 2`
    if test "$fs"
    then
	rm $fs
    fi
    echo "delete `echo "$fs" | wc -w` files: "$fs
fi


# Download and convert the sitemap
if test ! -f $OUTPUT_DIR/sitemap.csv
then
    echo "Extract sitemap: $SITEMAP"
    wget -q $SITEMAP -O - | ${SITE}_extract_sitemap "$SITEMAP" > $OUTPUT_DIR/sitemap.csv
fi


# Download and convert first-level pages (debate pages)
urls=`grep -v '^#' $OUTPUT_DIR/sitemap.csv | cut -d ';' -f 1 | sed 's/^.*://' | sort`
n_threads=0
for url in $urls
do
    local_filename=$OUTPUT_DIR/`num_of "$url"`.csv
    if test ! -f $local_filename
    then
	echo "Extract main page $local_filename: $url"
	(wget -q "$URL/$url" -O - | ${SITE}_extract_page "$URL" "$url") > $local_filename &
	n_threads=`expr $n_threads + 1`
	if test $n_threads -ge $N_THREADS
	then
	    wait -n
	    n_threads=`expr $n_threads - 1`
	fi
    fi
done
wait



# Download and convert all pages (iterate until no new page is downloaded)
n_files1=0
n_files2=`ls $OUTPUT_DIR/*.csv | wc -w`
indent="."
while test $n_files1 -ne $n_files2
do
    echo "${indent}Read urls"
    urls=`grep -v '^#' $OUTPUT_DIR/*.csv  | cut -d ';' -f 1 | sed 's/^.*://' | sort`

    echo "${indent}Seek files"
    n_threads=0
    for url in $urls
    do
	local_filename=$OUTPUT_DIR/`num_of "$url"`.csv
	if test ! -f $local_filename
	then
	    echo "${indent}Extract subpage $local_filename: $url"
	    (wget -q "$URL/$url" -O - | ${SITE}_extract_subpage "$URL" "$url") > $local_filename &

	    n_threads=`expr $n_threads + 1`
	    if test $n_threads -ge $N_THREADS
	    then
		wait -n
		n_threads=`expr $n_threads - 1`
	    fi
	fi
    done
    wait
    n_files1=$n_files2
    n_files2=`ls $OUTPUT_DIR/*.csv | wc -w`
    indent="$indent."
done





# Build the xxx_nodes.csv and xxx_edges.csv graph representation
echo "Create '${OUTPUT_DIR}_nodes.csv' and '${OUTPUT_DIR}_edges.csv'"
python3 mk_graph.py $OUTPUT_DIR


# Generate the Cypher insertion instructions for Neo4j
echo "Generate insert instructions (cypher)"
f=${OUTPUT_DIR}_insertion.cql
echo "// Auto-generated insertion instructions." > $f
tail -n +3 insertion_template.cql | sed "s/xxx/$OUTPUT_DIR/g" >> $f
