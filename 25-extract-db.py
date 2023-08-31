
import zipfile
import os
import shutil

def unzip_file(zip_path, extract_to='/tmp/'):
    print(f"Unzipping {zip_path} to {extract_to}")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def move_file(src, dest):
    print(f"Moving {src} to {dest}")
    shutil.move(src, dest)

def rezip_folder(folder_path, zip_name):
    print(f"Rezipping contents of {folder_path} to {zip_name} (excluding Brain.db)")
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file != 'Brain.db':
                    zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), folder_path))

def main(input_zip='Brain-pruned.zip', output_zip='content.zip'):
    temp_dir = '/tmp/brain_pruned_extraction'
    os.makedirs(temp_dir, exist_ok=True)
    unzip_file(input_zip, temp_dir)
    move_file(f'{temp_dir}/Brain.db', './Brain.db')
    rezip_folder(temp_dir, output_zip)
    print(f"Cleaning up {temp_dir}")
    shutil.rmtree(temp_dir)

if __name__ == '__main__':
    import sys
    input_zip = sys.argv[1] if len(sys.argv) > 1 else 'Brain-pruned.zip'
    output_zip = sys.argv[2] if len(sys.argv) > 2 else 'content.zip'
    main(input_zip, output_zip)
