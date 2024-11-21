import os
import shutil
import json
import argparse

def move_files_to_delete_folder(file_path, delete_folder_root, current_level):
    # Create corresponding path in "to delete" folder
    relative_path = os.path.relpath(os.path.dirname(file_path), delete_folder_root)
    delete_folder_path = os.path.join(delete_folder_root, "to delete", relative_path)
    os.makedirs(delete_folder_path, exist_ok=True)
    
    # Move the file to the "to delete" folder
    new_path = os.path.join(delete_folder_path, os.path.basename(file_path))
    try:
        shutil.move(file_path, new_path)
        # Store the original path in the JSON structure at the correct folder level
        current_level[os.path.basename(file_path)] = {
            "type": "file",
            "original_path": file_path
        }
        print(f"Moved: {file_path} -> {new_path}")
    except FileNotFoundError:
        print(f"File not found, skipping: {file_path}")


def get_rvt_files(folder_path):
    rvt_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            # Only consider original Revit files (not backups)
            if file.endswith(".rvt") and not (file[-8:-4].isdigit() and file[-9] == "."):  
                rvt_files.append(os.path.join(root, file))
                print(f"Found Revit file: {os.path.join(root, file)}")
    return rvt_files


def get_backup_files(folder_path, rvt_files):
    backup_files = []
    processed_files = set()
    for rvt_file in rvt_files:
        rvt_name = os.path.basename(rvt_file).rsplit('.', 1)[0]
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.startswith(rvt_name) and file.endswith('.rvt') and file.split('.')[-2].isdigit() and len(file.split('.')[-2]) == 4:
                    full_path = os.path.join(root, file)
                    if full_path not in processed_files:
                        backup_files.append(full_path)
                        processed_files.add(full_path)
                        print(f"Found backup file: {full_path}")
    return backup_files


def process_folders_recursively(current_path, delete_folder_root, json_data):
    # Normalize the relative path
    relative_path = os.path.relpath(current_path, delete_folder_root)
    relative_path = os.path.normpath(relative_path)

    # Split the relative path into its components (folders)
    folder_parts = relative_path.split(os.sep)

    # Navigate through json_data to the correct folder level
    current_level = json_data
    for part in folder_parts:
        if part == ".":
            continue  # Skip the root reference
        if part not in current_level:
            current_level[part] = {
                "type": "folder",
                "contents": {}
            }
        current_level = current_level[part]["contents"]

    # Process subfolders recursively
    for item in os.listdir(current_path):
        item_path = os.path.join(current_path, item)
        if os.path.isdir(item_path) and "to delete" not in item_path:
            # Recursively process the subfolder
            process_folders_recursively(item_path, delete_folder_root, json_data)
        elif os.path.isfile(item_path):
            # If it's a backup file, add it to the current folder in JSON and move it
            if item_path.endswith(".rvt") and (item_path[-8:-4].isdigit() and item_path[-9] == "."):
                move_files_to_delete_folder(item_path, delete_folder_root, current_level)


def save_json(json_data, delete_folder_root):
    json_path = os.path.join(delete_folder_root, "to_delete_files.json")
    with open(json_path, "w") as json_file:
        json.dump(json_data, json_file, indent=4)
    print(f"JSON data saved to {json_path}")

def restore_file(file_name, delete_folder_root, full_path=False):
    json_path = os.path.join(delete_folder_root, "to_delete_files.json")
    if not os.path.isfile(json_path):
        print("No JSON file found to restore from.")
        return
    
    with open(json_path, "r") as json_file:
        json_data = json.load(json_file)
    
    def find_file_in_json(data, file_name, full_path):
        for key, value in data.items():
            if value["type"] == "file":
                if full_path and value["original_path"] == file_name:
                    return value["original_path"]
                elif not full_path and key == file_name:
                    return value["original_path"]
            elif value["type"] == "folder":
                result = find_file_in_json(value["contents"], file_name, full_path)
                if result:
                    return result
        return None
    
    original_path = find_file_in_json(json_data, file_name, full_path=full_path)
    if original_path:
        current_path = os.path.join(delete_folder_root, "to delete", os.path.relpath(os.path.dirname(original_path), delete_folder_root), os.path.basename(original_path))
        if os.path.exists(current_path):
            os.makedirs(os.path.dirname(original_path), exist_ok=True)
            shutil.move(current_path, original_path)
            print(f"Restored: {current_path} -> {original_path}")
            # Check if the folder is empty and delete if it is
            clean_empty_folders(os.path.dirname(current_path), delete_folder_root)
        else:
            print(f"File {file_name} not found in delete folder.")
    else:
        print(f"File {file_name} not found in JSON data.")

def clean_empty_folders(folder_to_check, delete_folder_root):
    while True:
        if folder_to_check == delete_folder_root or not os.path.exists(folder_to_check):
            break
        if not os.listdir(folder_to_check):
            os.rmdir(folder_to_check)
            print(f"Deleted empty folder: {folder_to_check}")
            folder_to_check = os.path.dirname(folder_to_check)
        else:
            break

def restore_all_files(data, delete_folder_root):
    for key, value in data.items():
        if value["type"] == "file":
            original_path = value["original_path"]
            current_path = os.path.join(delete_folder_root, "to delete", os.path.relpath(os.path.dirname(original_path), delete_folder_root), key)
            if os.path.exists(current_path):
                os.makedirs(os.path.dirname(original_path), exist_ok=True)
                shutil.move(current_path, original_path)
                print(f"Restored: {current_path} -> {original_path}")
                # Check if the folder is empty and delete if it is
                clean_empty_folders(os.path.dirname(current_path), delete_folder_root)
        elif value["type"] == "folder":
            restore_all_files(value["contents"], delete_folder_root)

def restore_all(delete_folder_root):
    json_path = os.path.join(delete_folder_root, "to_delete_files.json")
    if not os.path.isfile(json_path):
        print("No JSON file found to restore from.")
        return
    
    with open(json_path, "r") as json_file:
        json_data = json.load(json_file)
    
    # Use the JSON data to restore all files
    if json_data:
        restore_all_files(json_data, delete_folder_root)
    else:
        print("No files found to restore.")

def restore_folder(folder_path, delete_folder_root):
    json_path = os.path.join(delete_folder_root, "to_delete_files.json")
    if not os.path.isfile(json_path):
        print("No JSON file found to restore from.")
        return
    
    with open(json_path, "r") as json_file:
        json_data = json.load(json_file)
    
    def restore_folder_files(data, folder_parts):
        current_level = data
        for part in folder_parts:
            if part in current_level:
                current_level = current_level[part]["contents"]
            else:
                print(f"Folder '{folder_path}' not found in JSON data.")
                return
        # Restore all files in the folder
        restore_all_files(current_level, delete_folder_root)

    # Split the folder path into its components relative to the root folder
    relative_path = os.path.relpath(folder_path, delete_folder_root)
    folder_parts = os.path.normpath(relative_path).split(os.sep)
    
    # Start from the root JSON level
    restore_folder_files(json_data, folder_parts)


def main():
    parser = argparse.ArgumentParser(description="Organize and manage Revit backup files.")
    parser.add_argument("-p", "--path", required=True, help="Path to the folder to organize")
    parser.add_argument("-m", "--move", action="store_true", help="Move files to delete folder")
    parser.add_argument("-r", "--restore", help="Restore a specific file")
    parser.add_argument("-rf", "--restore_folder", help="Restore a specific folder")
    parser.add_argument("-ra", "--restore_all", action="store_true", help="Restore all files")
    args = parser.parse_args()

    user_input_folder = args.path

    if not os.path.isdir(user_input_folder):
        print("The provided path is not a valid folder.")
        return

    delete_folder_root = os.path.abspath(user_input_folder)
    
    if args.move:
        json_data = {}
        process_folders_recursively(user_input_folder, delete_folder_root, json_data)
        save_json(json_data, delete_folder_root)
        print("File organization complete.")
    elif args.restore:
        restore_file(args.restore, delete_folder_root, full_path=True)
    elif args.restore_folder:
        restore_folder(args.restore_folder, delete_folder_root)
    elif args.restore_all:
        restore_all(delete_folder_root)
    else:
        print("Invalid action. Please specify an action using the command line arguments.")

if __name__ == "__main__":
    main()
