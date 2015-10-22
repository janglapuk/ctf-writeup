#!/bin/bash
set -e


SESSION_DIR=/var/sessions
mkdir -p $SESSION_DIR


function explode {
    IFS="$1" read -ra "$2" <<< "$3"
}


function filter_nonalpha {
    echo $(echo $1 | sed 's/[^a-zA-Z0-9.!$;?_]//g')
}


function parse {
    explode '&' 'pairs' "$1"
    for pair in "${pairs[@]}"; do
        explode '=' 'keyval' "$pair"
        export $(filter_nonalpha "${keyval[0]}")="${keyval[1]}"
    done
}


if [ -v QUERY_STRING ]; then
    parse "$QUERY_STRING"
fi


declare -A headers
headers["Content-Type"]="text/html; charset=UTF-8"
headers["X-Frame-Options"]="DENY"
headers["Content-Security-Policy"]="default-src 'none'"


function flush_headers {
    for header in "${!headers[@]}"; do
        echo -ne "$header: ${headers[$header]}\r\n"
    done
    echo -ne "\r\n"
}

if [ ! -v sessid ]; then
    headers["Location"]="?sessid=$(head -c 32 /dev/urandom | xxd -ps)"
    flush_headers
    exit
fi
sessid=$(filter_nonalpha $sessid)
if [ -z $sessid ] || [ "${#sessid}" -lt 60 ]; then
    echo 'like... really?'
    exit
fi
sessfile=$SESSION_DIR/$sessid
if [ -f $sessfile ]; then
    explode '#' 'messages' "$(cat $sessfile)"
else
    messages=()
fi


if [ ! -v page ]; then
    page=home
else
    page=$(filter_nonalpha "$page")
fi
if [[ "$page" == "index" ]]; then
    page=home
fi
file="$DOCUMENT_ROOT/$page.sh"
if [ ! -f $file ]; then
    >&2 echo "Can't load $file"
    file="$DOCUMENT_ROOT/404.sh"
fi
source $file


flush_headers


if [ -v DEBUG ]; then
    echo -ne '<pre>'
    printenv
    echo -ne '</pre>'
fi


case "$REQUEST_METHOD" in
"GET")
    get
    ;;
"POST")
    post
    ;;
esac


if [ ! -z "$messages" ]; then
    echo -ne "" > $sessfile
    for msg in "${messages[@]}"; do
        echo -ne "$(filter_nonalpha $msg)#" >> $sessfile
    done
fi
