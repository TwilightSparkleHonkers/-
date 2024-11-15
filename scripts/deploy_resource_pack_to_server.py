import os
import json
import hashlib
import requests
import subprocess
import shutil

# Hardcoded SSH and server details
SSH_HOST = "acer"
# SSH_USERNAME = "your_ssh_user"
# SSH_KEY_PATH = "~/.ssh/id_rsa"  # Adjust this to your SSH key path
SERVER_PROPERTIES_PATH = "~/minecraft_servers/fabric_1.21.1_mods_tests/server.properties"

# Paths and configuration
RESOURCEPACK_SRC = "TwinkleResourcePack"
CONFIG_FILE = "config.json"
ZIP_FILENAME = "resourcepack.zip"
WEBHOOK_URL =  "https://discord.com/api/webhooks/1306769223707525200/yXERVimBNbKp1_pfEDTqm9t45KQzgEhP_SvsUvEZ7W0CYOPe7uhqOlDvJlrC6kpZ0qHv"

# Zip the resource pack directory using PowerShell's Compress-Archive
def zip_resource_pack():
    if not os.path.exists(RESOURCEPACK_SRC):
        print(f"Resource pack folder {RESOURCEPACK_SRC} does not exist.")
        return None
    
    # Remove existing zip file if it exists
    if os.path.exists(ZIP_FILENAME):
        os.remove(ZIP_FILENAME)

    # Use PowerShell's Compress-Archive command to create the zip
    zip_command = [
        "powershell", "-Command",
        f"Compress-Archive -Path {RESOURCEPACK_SRC}/* -DestinationPath {ZIP_FILENAME}"
    ]
    result = subprocess.run(zip_command, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Failed to zip the resource pack: {result.stderr}")
        return None

    print(f"Zipped {RESOURCEPACK_SRC} to {ZIP_FILENAME}")
    return ZIP_FILENAME

# Calculate SHA1 hash of the file
def calculate_sha1(file_path):
    sha1 = hashlib.sha1()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            sha1.update(chunk)
    return sha1.hexdigest()

# Upload zip file to Discord webhook
def upload_to_discord(zip_path, webhook_url):
    with open(zip_path, 'rb') as file:
        response = requests.post(
            webhook_url,
            files={'file': (ZIP_FILENAME, file)}
        )
        if response.status_code == 200:
            json_response = response.json()
            try:
                attachments = json_response.get("attachments", [])
                if attachments:
                    download_url = attachments[0].get("url")
                    # escaped_url = download_url.replace("&", "^&")
                    print(f"Uploaded successfully. Download URL: {download_url}")
                    return download_url
                else:
                    print("Failed to retrieve the download URL from response.")
                    return None
            except Exception as e:
                print(f"Error parsing Discord response: {e}")
                return None
        else:
            print(f"Failed to upload to Discord. Status Code: {response.status_code}")
            return None

# Update server.properties via SSH using sed
def update_server_properties(download_url, sha1_hash):

    # # Enclose the URL in double quotes to avoid PowerShell parsing issues
    # quoted_url = f'{download_url}'
    
    # Bash command to update server.properties
    bash_command = (
        f"sed -i '/^resource-pack=/d' {SERVER_PROPERTIES_PATH} && "  # Remove existing resource-pack line
        f"sed -i '/^resource-pack-sha1=/d' {SERVER_PROPERTIES_PATH} && "  # Remove existing resource-pack-sha1 line
        f"echo 'resource-pack={download_url}' >> {SERVER_PROPERTIES_PATH} && "  # Add new resource-pack line with quoted URL
        f"echo 'resource-pack-sha1={sha1_hash}' >> {SERVER_PROPERTIES_PATH}"  # Add new resource-pack-sha1 line
    )

    # print(bash_command)

    ssh_command = f"ssh {SSH_HOST} \"{bash_command}\""

    print(f"Updating server properties via SSH...")
    result = subprocess.run(
        ["powershell", "-Command", ssh_command],
        capture_output=True,
        text=True
    )

    # Print the output from the SSH command to help debug
    print(f"SSH command output: {result.stdout}")
    print(f"SSH command error (if any): {result.stderr}")

    if result.returncode == 0:
        print("Server properties updated successfully.")
    else:
        print(f"Failed to update server properties. Error: {result.stderr}")

# Main function
def main():

    # Zip the resource pack
    zip_path = zip_resource_pack()
    if not zip_path:
        return

    # Calculate SHA1
    sha1_hash = calculate_sha1(zip_path)
    print(f"SHA1 Hash: {sha1_hash}")

    # Upload to Discord
    download_url = upload_to_discord(zip_path, WEBHOOK_URL)
    if not download_url:
        return

    # Update server.properties via SSH
    update_server_properties(download_url, sha1_hash)

if __name__ == "__main__":
    main()