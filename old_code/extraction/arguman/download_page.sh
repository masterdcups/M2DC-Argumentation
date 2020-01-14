#! /bin/sh

# This script download pages from Argüman
# (recursively download partial data)
# and change some part of html to make it valid wrt. xsltproc



# Check command-line args
usage() {
    echo "$0: usage: $0 url output" >&2
}

test $# -ne 2 && usage && exit 1
url="$1"
output="$2"


tmp="$output.tmp"
tmp2="$output.tmp2"

# Download page
wget -q "$url" -O "$tmp"

# Check if partial data are missing
while test "`grep "data-load-partial" "$tmp"`"
do
    grep -n 'data-load-partial' "$tmp" | while read line
    do
	num="`echo "$line" | cut -d ':' -f 1`"
	url2="`echo "$line" | sed 's/^.*"\(.*\)".*$/\1/'`"
	echo "$output: partial data <- $url2"
	data="`wget -q "$url$url2" -O -`"
	head -n `expr $num - 1` "$tmp" > "$tmp2"
	echo "$data" >> "$tmp2"
	tail -n +`expr $num + 1` "$tmp" >> "$tmp2"
	cat "$tmp2" > "$tmp"
	break
    done
done
cat "$tmp" > "$output"
rm -f "$tmp" "$tmp2"

exit 0
