#!/bin/bash


DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )


function get {
    cat $DIR/home.html
    echo -ne '<ul>'
    for msg in "${messages[@]}"; do
        echo -ne "<li>$msg</li>"
    done
    echo -ne '</ul>'
}


function post {
    data=$(head -c $CONTENT_LENGTH)
    parse "$data"
    msg="$(filter_nonalpha \"$msg\")"
    if [ ! -z $msg ]; then
        messages+=($msg)
    fi
    get
}
