# RVT Organizer

RVT Organizer is a Python-based script designed to help you manage Revit backup files efficiently. It automatically organizes, moves, and restores Revit backup files (.rvt) based on user-defined actions, simplifying file management for large projects.

## Features

- **Move Revit Backup Files**: Identify and move Revit backup files (“.filename.extension” format with a specific pattern) to a separate folder for easier organization.
- **JSON-Based Storage of File Information**: Keeps track of moved files and their original locations in a JSON file for seamless restoration.
- **Restore Individual Files or Folders**: Restore files or entire folders from the "to delete" directory to their original locations using the JSON information.
- **Command-Line Arguments for Flexibility**: Supports multiple command-line arguments for different operations (moving, restoring, etc.).

## How It Works

1. **Move Backup Files**: When executed, RVT Organizer will recursively search the provided folder path for Revit backup files and move them to a designated "to delete" folder.
2. **Generate a JSON File**: The details of all moved files are stored in a JSON file (`to_delete_files.json`). This helps in keeping a record of each file's original location for restoration purposes.
3. **Restore Files or Folders**: You can restore either specific files or entire folders from the "to delete" folder to their original locations by referencing the JSON file.

## Command-Line Usage

The script offers a variety of options to manage Revit files effectively. Below are the available command-line arguments:

- `-p, --path`: **(Required)** Specify the path to the folder that needs to be organized.
- `-m, --move`: Move Revit backup files to the "to delete" folder.
- `-r, --restore`: Restore a specific file. Provide the full path of the file to restore it to its original location.
- `-rf, --restore_folder`: Restore a specific folder. Provide the path of the folder to restore all files within it.
- `-ra, --restore_all`: Restore all files from the "to delete" folder.

### Examples

- **Move Revit Backup Files**:
  ```
  python3 rvt_organizer.py -p "Nova pasta" -m
  ```
  This will move all Revit backup files from the specified folder ("Nova pasta") to the "to delete" folder.

- **Restore a Single File**:
  ```
  python3 rvt_organizer.py -p "Nova pasta" -r "Nova pasta/Projeto 01/Ante Projeto/AP.0001.rvt"
  ```
  This command will restore the specified backup file to its original location.

- **Restore a Folder**:
  ```
  python3 rvt_organizer.py -p "Nova pasta" -rf "Nova pasta/Projeto 01/Ante Projeto"
  ```
  This will restore all files in the "Ante Projeto" folder to their original locations.

- **Restore All Files**:
  ```
  python3 rvt_organizer.py -p "Nova pasta" -ra
  ```
  This will restore all files that were previously moved to the "to delete" folder.

## JSON File

The JSON file (`to_delete_files.json`) stores the structure of all moved files, including their original paths. Here's an example of how the JSON file is structured:

```json
{
  "Projeto 01": {
    "type": "folder",
    "contents": {
      "Ante Projeto": {
        "type": "folder",
        "contents": {
          "AP.0001.rvt": {
            "type": "file",
            "original_path": "Nova pasta/Projeto 01/Ante Projeto/AP.0001.rvt"
          }
        }
      }
    }
  }
}
```

This structure ensures that you can easily trace and restore any files that were moved by the script.

## Prerequisites

- **Python 3**: Ensure that Python 3 is installed on your system.
- **argparse**: This library is used to handle command-line arguments and is part of Python's standard library.

## Installation

To get started, clone this repository and make sure all required dependencies are installed. No external libraries are required beyond Python's standard library.

```bash
git clone <repository_url>
cd RVT_Organizer
```

## Notes

- The folder structure in the "to delete" folder mirrors the original structure of the organized folder, which makes it easier to locate and restore files.
- Only Revit backup files (with numeric sequences and a `.rvt` extension) are moved to the "to delete" folder, ensuring the original Revit files are kept intact.

## Troubleshooting

- **File Not Found Errors**: Ensure that the paths specified are correct and that the folder structure has not changed after the move operation.
- **Restoring Files**: Restoring requires the JSON file to be present and valid. Make sure `to_delete_files.json` is available in the folder.

## License

This project is licensed under the MIT License. Feel free to use and modify it as needed.

## Contributions

Contributions are welcome! Please open an issue or submit a pull request if you have suggestions or improvements.

## Authors

Developed by Matheus Farnetani.

For more questions, feel free to reach out!

