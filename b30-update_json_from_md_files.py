
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
    
    # Initialize counter and list for matched entries
    captured_string_counter = Counter()
    matched_entries = []
    formatted_entries = []

    # Search and capture
    for md_file in md_files:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        for match, captured in phrase_pattern.findall(content):
            if len(captured) >= 3:
                captured_string_counter[captured] += 1
                matched_entries.append(f"[{match}] {captured}")
                formatted_entries.append(f"{match} [{captured}](#wdid=PLACEHOLDER)")
                
    # Read JSON
    with open('./wikidata-lookup.json', 'r', encoding='utf-8') as f:
        wikidata_lookup = json.load(f)
        
    # Add missing keys and print matched entries with WikidataId
    not_found_keys = []
    printed_count = 0
    for captured in captured_string_counter.keys():
        key_lower = captured.lower()
        if key_lower not in (key.lower() for key in wikidata_lookup.keys()):
            not_found_keys.append(captured)
            wikidata_lookup[key] = None
        else:
            # Replace PLACEHOLDER in formatted_entries with actual WikidataId for the first 10 entries
            wikidataId = wikidata_lookup[next(key for key in wikidata_lookup.keys() if key.lower() == key_lower)]
            if wikidataId and printed_count < 10:
                formatted_entries[printed_count] = formatted_entries[printed_count].replace("PLACEHOLDER", wikidataId)
                printed_count += 1

    # Save updated JSON
    with open('./wikidata-lookup.json', 'w', encoding='utf-8') as f:
        json.dump(wikidata_lookup, f, ensure_ascii=False, indent=4)

    # Print first 5 formatted entries as samples
    print("Sample Formatted Entries:")
    for entry in formatted_entries[:5]:
        print(entry)

if __name__ == "__main__":
    main()
