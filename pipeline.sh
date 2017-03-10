#!/bin/bash

function remove_existing_db {
    if [ -s $1 ]; then
        echo are you sure you want to remove $1 ?
        read
        rm $1 || true
    fi
}

remove_existing_db mlb.db
python3 scrape.py
