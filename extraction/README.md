# Extraction

## Requesting from Wikidebats using the MediaWiki API

Requesting the pages in the category "Débats construits", and downloading the html of the first one. A prettified version can be found in `debat_pretty.html`.
```
pip install requests
python3 extraction_debats.py
```

## Parsing the html
Load the html tree and try to find the names of arguments for the cause.
The html structure of wikidebats is not easy to work with.
```
pip install lxml
python3 tree.py
```
