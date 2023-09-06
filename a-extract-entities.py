
import json
import re
import zipfile
import os
from collections import Counter

# Read the relationship-names.txt file from the current directory
with open('./relationship-names.txt', 'r') as f:
    relationship_names = f.readlines()

# Remove newline characters and surround each string with square brackets
relationship_names = [f"[{{name.strip()}}]" for name in relationship_names]

# Unzip the content.zip file into the specified directory
with zipfile.ZipFile('../content.zip', 'r') as zip_ref:
    zip_ref.extractall('./unzipped_content/')

# List .md files recursively
md_files = []
for root, dirs, files in os.walk('./unzipped_content/'):
    for file in files:
        if file.endswith(".md"):
            md_files.append(os.path.join(root, file))

# Initialize a new Counter to store the counts of each comprehensive entity
comprehensive_entity_count = Counter()

# Define a regular expression pattern to match a relationship name followed by a space and then a letter
pattern_template = r"{{}} (?P<entity>[A-Za-z\s\-]+)"

# Search for relationship names in each .md file
for md_file in md_files:
    with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    for name in relationship_names:
        pattern = re.compile(pattern_template.format(re.escape(name)))
        matches = pattern.findall(content)
        # Filter out entities that don't start with a capital letter
        comprehensive_entities = [match.strip() for match in matches if match.strip()[0].isupper()]
        comprehensive_entity_count.update(comprehensive_entities)

# Sort the entities by occurrence counts in descending order
sorted_entities = [entity for entity, _ in comprehensive_entity_count.most_common()]

# Create the JSON object with sorted entities as keys and values set to null
sorted_entities_json = {{entity: None for entity in sorted_entities}}

# Output the JSON object
print(json.dumps(sorted_entities_json, ensure_ascii=False, indent=4))

# Save the JSON object to a file
with open('./a-entities.json', 'w') as f:
    json.dump(sorted_entities_json, f, ensure_ascii=False, indent=4)
