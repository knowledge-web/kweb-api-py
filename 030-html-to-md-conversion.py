import os
import zipfile
import shutil
from bs4 import BeautifulSoup
import markdown  # Make sure to install this library

# Define paths
input_zip_path = './Brain.zip'
unzip_dir = '/tmp/unzipped_data'
output_zip_path = './Brain.zip'

# Unzip the file
with zipfile.ZipFile(input_zip_path, 'r') as zip_ref:
    zip_ref.extractall(unzip_dir)

# Initialize variables
folders_to_convert = []
remaining_html_count = 0

# Identify folders to convert
for root, dirs, files in os.walk(unzip_dir):
    has_html = 'notes.html' in files
    has_md = 'Notes.md' in files

    if has_html and not has_md:
        folders_to_convert.append(root)

    if has_html:
        remaining_html_count += 1

# Convert HTML to Markdown
for folder in folders_to_convert:
    html_path = os.path.join(folder, 'notes.html')
    md_path = os.path.join(os.path.dirname(folder), 'Notes.md')

    with open(html_path, 'r', encoding='utf-8') as html_file:
        html_content = html_file.read()

    # Convert HTML to Markdown using BeautifulSoup and markdown library
    soup = BeautifulSoup(html_content, 'html.parser')
    md_content = markdown.markdown(soup.get_text())

    with open(md_path, 'w', encoding='utf-8') as md_file:
        md_file.write(md_content)

    os.remove(html_path)

    if not os.listdir(folder):
        os.rmdir(folder)

# Re-zip the directory
shutil.make_archive(output_zip_path[:-4], 'zip', unzip_dir)
