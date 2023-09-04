# TODO wget https://k-web.ismandstory.com/api/v0/Brain-master.zip <-- make this work, also configurable with an API url?
# Though this Replit is public? 🤔

# cp orig/Brain-master.zip Brain-master.zip
# python 10-kweb-export-to-normal.py
cp orig/Brain-no-media--debug.zip Brain.zip # Do this, skip first step and work w. smaller (debug) files
python 20-brain-remove-forgotten.py Brain.zip Brain-pruned.zip
python 30-kweb-name-extractor.py Brain-pruned.zip
python 40-kweb-wikilink-extractor.py Brain-pruned.zip
# TODO kweb-wikilink-finder.py - used node.Name & metaName from above 
# TODO kweb-wikidataid-finder.py
# TODo kweb-wikidata-cache...

python 95-link-names-from-json.py wikidata-link.json