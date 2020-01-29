#! /bin/sh


# Globals
VERBOSE=""




# Parse command-line arguments

usage() { # $1=msg
    echo "$0: usage: $0 site_id [-v|--verbose]" >&2
    test "$1" && echo "$0: $1" >&2
}
if test $# -lt 1
then
    usage
    exit 1
fi
case "$1" in
    wd | am-* | kl)
    ;;
    *)
	usage "site_id must be in {wd, am-*, kl}"
	exit 2
	;;
esac
case $# in
    1)
	;;
    2)
	case "$2" in
	    -v | --verbose)
		VERBOSE=1
		;;
	    *)
		usage "Unrecognized option $2"
		exit 3
		;;
	esac
	;;
    *)
	usage
	exit 4
	;;
esac

		

SRC_EDGES="$1_edges.csv"
SRC_NODES="$1_nodes.csv"



# Check doubles in keys (nodes.csv)
check_node_keys() {
    action=""
    test "$VERBOSE" && action='print "Duplicate key: " $1;'
    cat $SRC_NODES \
	| awk -F ',' 'BEGIN{n_errors=0} {arr[$1] += 1; if (arr[$1] > 1){ '"$action"' n_errors+=1; }} END{ print "'"$SRC_NODES"': " n_errors " duplicate keys";}'
}

check_node_values() {
    action=""
    test "$VERBOSE" && action='print "Node without text: " $0;'
    cat $SRC_NODES \
	| awk -F ',' 'BEGIN{n_errors=0} {n+=1; if ($3 == "\"\"") { '"$action"' n_errors+=1; } n += 1} END{ print "'"$SRC_NODES"': " n_errors " empty labels";}'
}

check_edge_keys() {
    action=""
    test "$VERBOSE" && action='print "Duplicate edge: (" $1 ", " $2 ")";'
    cat $SRC_EDGES \
	| awk -F ',' 'BEGIN{n_errors=0} {arr[$1][$2] += 1; if (arr[$1][$2] > 1) { '"$action"' n_errors+=1; }} END{ print "'"$SRC_EDGES"': " n_errors " duplicate links";}'
}

check_edge_values() {
    action=""
    test "$VERBOSE" && action='print "No weight for the edge " $0;'
    cat $SRC_EDGES \
	| awk -F ',' 'BEGIN{n_errors=0} {if ($3 == "") { '"$action"' n_errors+=1; }} END{ print "'"$SRC_EDGES"': " n_errors " empty weights";}'
}

check_node_keys
check_node_values
check_edge_keys
check_edge_values
