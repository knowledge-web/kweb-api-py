
import zipfile
import json
import os
import re
from collections import Counter

def main():
    # Unzip content.zip
    unzip_dir = './content_unzipped'
    os.makedirs(unzip_dir, exist_ok=True)
    
    with zipfile.ZipFile('./content.zip', 'r') as zip_ref:
        zip_ref.extractall(unzip_dir)

    # List markdown files
    md_files = []
    for root, dirs, files in os.walk(unzip_dir):
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))
                
    # Read phrases from link-names.txt
    with open('./link-names.txt', 'r') as f:
        phrases = f.readlines()
    phrases = [phrase.strip().strip('[]') for phrase in phrases]
    
    # Compile regex pattern
    phrase_pattern = re.compile(r'\[(%s)\] ([\w\s\-\&]+)[^\w\s\-\&\n]' % '|'.join(re.escape(phrase) for phrase in phrases))
    
    # Initialize counter
    captured_string_counter = Counter()

    # Search and capture
    for md_file in md_files:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        for match, captured in phrase_pattern.findall(content):
            if len(captured) >= 3:
                captured_string_counter[captured] += 1
                
    # Read JSON
    with open('./wikidata-lookup.json', 'r', encoding='utf-8') as f:
        wikidata_lookup = json.load(f)
        
    # Add missing keys
    not_found_keys = []
    for captured in captured_string_counter.keys():
        if captured.lower() not in (key.lower() for key in wikidata_lookup.keys()):
            not_found_keys.append(captured)
    
    for key in not_found_keys:
        wikidata_lookup[key] = None

    # Save updated JSON
    with open('./wikidata-lookup.json', 'w', encoding='utf-8') as f:
        json.dump(wikidata_lookup, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
