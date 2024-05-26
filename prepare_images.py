import os
import shutil
from tqdm import tqdm

from convert_files.heic_to_png import convert_heic_to_png
from convert_files.jpg_to_png import convert_jpg_to_png

def prepare_images(input_folder_path, converted_files_output_directory):

    # Get a list of all files in the directory
    all_files = os.listdir(input_folder_path)

    # Iterate over each file in the directory
    for filename in tqdm(all_files, desc="Converting images"):

        #print(f"[VAR] filename: {filename}")

        filename_without_ext = os.path.splitext(filename)[0]

        file_path = os.path.join(input_folder_path, filename)

        converted_file_path = os.path.join(converted_files_output_directory, f"{filename_without_ext}.png")

        # Check if the file has already been converted
        if os.path.exists(converted_file_path):
            #print(f"[INFO] File {filename} has already been converted, skipping...")
            continue

        if filename.lower().endswith(".heic"):
            convert_heic_to_png(file_path, converted_files_output_directory)

        if filename.lower().endswith(".jpg"):
            convert_jpg_to_png(file_path, converted_files_output_directory)

        if filename.lower().endswith(".png"):
            shutil.copy(file_path, converted_files_output_directory)
            
    print("\n[INFO] Images prepared.")