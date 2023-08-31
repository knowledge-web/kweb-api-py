# cp orig/Brain-master.zip Brain-master.zip
# python 10-kweb-export-to-normal.py
cp orig/Brain-no-media--debug.zip Brain.zip # Do this, skip first step and work w. smaller (debug) files
python 20-brain-remove-forgotten.py Brain.zip Brain-pruned.zip
python 30-kweb-name-extractor.py Brain-pruned.zip
python 40-kweb-wikilink-extractor.py Brain-pruned.zip
# TODO kweb-wikilink-finder.py - used node.Name & metaName from above 
# TODO kweb-wikidataid-finder.py
# TODo kweb-wikidata-cache...