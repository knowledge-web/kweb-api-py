# TODO wget https://k-web.ismandstory.com/api/v0/Brain-master.zip <-- make this work, also configurable with an API url?

# cp orig/Brain-master.zip Brain-master.zip
# python 010-kweb-export-to-normal.py
cp orig/Brain-no-media--debug.zip Brain.zip # Do this, skip first step and work w. 
python 020-brain-remove-forgotten.py
python 030-html-to-md-conversion.py
python 040-extract-db.py
python 045-brain-link-types.py
python 050-new-db.py
python 060-name-extractor.py
python 070-wikilink-extractor.py
python 080-md-replace-brain-links.py
python 090-wiki-search-script.py
python 100-wikidata-search-script.py
python 110-wikidata-search-by-name-script.py
python 120-link-names-from-json.py
python 130-make-wikidata-cache.py
python 140-wikidata-links-generator.py
python 120-link-names-from-json.py ./wikidata-links.json