
import os
import re
import base64
import uuid
import zipfile
import tempfile
import shutil

# Function to rearrange and swap bytes to convert to correct UUID format
def rearrange_and_swap_bytes(decoded_bytes):
    time_low = decoded_bytes[0:4][::-1]
    time_mid = decoded_bytes[4:6][::-1]
    time_hi_version = decoded_bytes[6:8][::-1]
    clock_seq_hi_res = decoded_bytes[8:10]
    node = decoded_bytes[10:]
    rearranged_bytes = time_low + time_mid + time_hi_version + clock_seq_hi_res + node
    decoded_uuid = str(uuid.UUID(bytes=rearranged_bytes))
    return decoded_uuid

# Function to replace brain links in the content of a file
def replace_brain_links(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    brain_link_pattern = r'brain://([a-zA-Z0-9_-]+)'
    brain_links = re.findall(brain_link_pattern, content)
    for link in brain_links:
        try:
            decoded_bytes = base64.urlsafe_b64decode(link + '==')
            uuid_str = rearrange_and_swap_bytes(decoded_bytes)
            content = content.replace(f'brain://{link}', f'#id={uuid_str}')
        except Exception as e:
            pass
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

# Function to further refine the converted links by removing extra parts after the IDs
def refine_converted_links(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    extra_parts_pattern = r'(#id=[a-f0-9\-]+)(/[\w\d]+)'
    modified_content, num_replacements = re.subn(extra_parts_pattern, r'\1', content)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(modified_content)

# Function to handle zip files
def handle_zip(input_zip_path, output_zip_path):
    with tempfile.TemporaryDirectory() as tmp_dir:
        with zipfile.ZipFile(input_zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmp_dir)
        for root, dirs, files in os.walk(tmp_dir):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    replace_brain_links(file_path)
                    refine_converted_links(file_path)
        with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
            for root, dirs, files in os.walk(tmp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, tmp_dir)
                    zip_ref.write(file_path, arcname)

# Example usage:
handle_zip('./content.zip', './content2.zip')
               