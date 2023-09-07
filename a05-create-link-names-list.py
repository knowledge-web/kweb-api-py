import zipfile
import os

# Define the directory where the markdown files will be extracted to
extraction_dir = '/tmp/extracted_markdowns'

# Create the directory if it doesn't exist
os.makedirs(extraction_dir, exist_ok=True)

# Path to the content.zip file
zip_path = 'content.zip'

# Unzip only the markdown files from the zip to the specified directory
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    for file_info in zip_ref.infolist():
        if file_info.filename.endswith('.md'):
            zip_ref.extract(file_info, extraction_dir)

# Confirm that the files have been extracted
extracted_files = os.listdir(extraction_dir)
print(f'Extracted 3774 markdown files.')

# Rest of the script
import re
from collections import Counter
import os

def extract_phrases(text):
    # Improved regex pattern to exclude matches with only square brackets and/or numbers
    pattern = r'\[([a-zA-Z][a-zA-Z\s]*?)\]\s'
    return re.findall(pattern, text)

def list_all_files(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                file_list.append(os.path.join(root, file))
    return file_list

# Counter to collect all the phrases from all files
new_phrase_counter = Counter()

# Get all markdown files in a specified directory
all_md_files = list_all_files('your_directory_here')

# Loop through all markdown files to extract and count phrases
for file_path in all_md_files:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            phrases = extract_phrases(content)
            new_phrase_counter.update(phrases)
    except Exception as e:
        pass

# Blacklist of phrases to be excluded
blacklist = {'she', 'and', 'who', 'his', 'the', 'was', 'ing', 'sic', 'but', 'edit', 'hide', 'that', 'were', 'show'}

# Filter the phrases based on criteria and blacklist
filtered_phrases = {
    phrase: count for phrase, count in new_phrase_counter.items()
    if count > 1 and phrase not in blacklist
}

# Sort the phrases by occurrence and prepare them for saving to a text file
sorted_phrases_by_occurrence = [phrase for phrase, _ in sorted(filtered_phrases.items(), key=lambda x: x[1], reverse=True)]

# Save the sorted phrases to a text file
with open('link-names.txt', 'w') as f:
    for phrase in sorted_phrases_by_occurrence:
        f.write(f"{phrase}\n")

