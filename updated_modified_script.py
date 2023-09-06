# Import necessary libraries
import os
import zipfile
import re
import spacy
nlp = spacy.load("en_core_web_md")

# Unzip the content.zip file into /tmp/
with zipfile.ZipFile('./content.zip', 'r') as zip_ref:
    zip_ref.extractall('/tmp/unzipped_content/')
  
# Define the directory where the unzipped .md files are stored
unzip_dir = '/tmp/unzipped_content/'

# List .md files recursively
md_files = []
for root, dirs, files in os.walk(unzip_dir):
    for file in files:
        if file.endswith(".md"):
            md_files.append(os.path.join(root, file))

# Read the relationship names from a text file (one name per line)
with open('./relationship-names.txt', "r") as f:
    relationship_names = f.readlines()

# Remove newline characters and surround each string with square brackets
relationship_names = [f"[{name.strip()}]" for name in relationship_names]

# Initialize a set to store extracted entities
extracted_entities = set()

# Regular expression pattern for checking if a string is followed by at least one space and a letter
pattern_suffix = r"\s+[a-zA-Z]"

# Search for relationship names in each .md file and extract entities
for md_file in md_files:
    with open(md_file, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    for name in relationship_names:
        for match in re.findall(f"{re.escape(name)}{pattern_suffix}\w+", content):
            # Extract text following the relationship name
            text_to_analyze = match[len(name):].strip()
            
            # Perform NER on the text
            doc = nlp(text_to_analyze)
            
            # Add the recognized entities to the set
            for ent in doc.ents:
                extracted_entities.add(ent.text)

# Save the extracted entities to a text file
with open("extracted_entities.txt", "w") as f:
    for entity in extracted_entities:
        f.write(f"{entity}\n")

# Count of total and unique entities
total_entities = len(extracted_entities)
unique_entities = len(set(extracted_entities))

print(f"NER extraction completed. Extracted entities saved to 'extracted_entities.txt'.")
print(f"Total entities extracted: {total_entities}")
print(f"Unique entities extracted: {unique_entities}")
