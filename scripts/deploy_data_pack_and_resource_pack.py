import os
import json
import shutil

# Paths for the data pack and resource pack in your repo
DATAPACK_SRC = "TwinkleDataPack"
RESOURCEPACK_SRC = "TwinkleResourcePack"

# Configuration file path
CONFIG_FILE = "scripts/config.json"

def load_config():
    # Load configuration file
    if not os.path.exists(CONFIG_FILE):
        print(f"Configuration file {CONFIG_FILE} not found.")
        return None
    with open(CONFIG_FILE, 'r') as file:
        try:
            config = json.load(file)
            return config
        except json.JSONDecodeError as e:
            print(f"Error reading {CONFIG_FILE}: {e}")
            return None

def copy_directory(src, dest):
    # Copy directory to destination
    if not os.path.exists(src):
        print(f"Source folder {src} does not exist.")
        return

    if not os.path.exists(dest):
        print(f"Destination folder {dest} does not exist.")
        return

    try:
        # If the folder already exists, remove it first
        if os.path.exists(os.path.join(dest, os.path.basename(src))):
            shutil.rmtree(os.path.join(dest, os.path.basename(src)))
        
        # Copy the source folder to the destination
        shutil.copytree(src, os.path.join(dest, os.path.basename(src)))
        print(f"Copied {src} to {dest}")
    except Exception as e:
        print(f"Failed to copy {src} to {dest}: {e}")

def main():
    config = load_config()
    if not config:
        return

    datapack_dest = config.get("datapack_path")
    resourcepack_dest = config.get("resourcepack_path")

    if datapack_dest:
        copy_directory(DATAPACK_SRC, datapack_dest)
    else:
        print("Datapack path not specified in the configuration file.")

    if resourcepack_dest:
        copy_directory(RESOURCEPACK_SRC, resourcepack_dest)
    else:
        print("Resource pack path not specified in the configuration file.")

if __name__ == "__main__":
    main()
