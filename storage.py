import json
import os
import sys
import shutil
import platform

def get_storage_path():
    """Returns the platform-specific path for storing application data."""
    app_name = "TempMailApp"
    if platform.system() == "Windows":
        base_dir = os.environ.get("APPDATA")
    elif platform.system() == "Darwin":
        base_dir = os.path.expanduser("~/Library/Application Support")
    else:
        # Fallback for Linux or other Unix systems
        base_dir = os.path.expanduser("~/.config")
    
    if not base_dir:
        # If for some reason APPDATA isn't set on Windows
        base_dir = os.path.expanduser("~")

    storage_dir = os.path.join(base_dir, app_name)
    
    # Ensure directory exists
    if not os.path.exists(storage_dir):
        try:
            os.makedirs(storage_dir, exist_ok=True)
        except Exception as e:
            print(f"Error creating storage directory: {e}")
            return "saved_emails.json" # Fallback to cwd
            
    storage_file = os.path.join(storage_dir, "saved_emails.json")
    
    # Seed with bundled data if persistent file doesn't exist
    if not os.path.exists(storage_file):
        # Check if we are bundled
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            bundled_data = os.path.join(sys._MEIPASS, "saved_emails.json")
            if os.path.exists(bundled_data):
                try:
                    shutil.copy2(bundled_data, storage_file)
                except Exception as e:
                    print(f"Failed to seed initial data: {e}")
                    
    return storage_file

STORAGE_FILE = get_storage_path()

def open_storage_folder():
    """Opens the folder containing the storage file in the OS file explorer."""
    import subprocess
    path = os.path.dirname(STORAGE_FILE)
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.run(["open", path])
    else:
        try:
            subprocess.run(["xdg-open", path])
        except:
            pass

def load_emails():
    """Loads the list of saved email addresses."""
    if not os.path.exists(STORAGE_FILE):
        return []
    try:
        with open(STORAGE_FILE, 'r') as f:
            data = json.load(f)
            return data.get("emails", [])
    except (json.JSONDecodeError, IOError):
        return []

def save_email(address, password):
    """Saves a new unique email address and password to storage."""
    emails = load_emails()
    # Avoid duplicates
    if any(e.get('address') == address for e in emails):
        return False
    
    emails.append({
        'address': address,
        'password': password
    })
    
    try:
        with open(STORAGE_FILE, 'w') as f:
            json.dump({"emails": emails}, f, indent=4)
        return True
    except IOError as e:
        print(f"Error saving to file: {e}")
        return False

def update_email_metadata(address, stage_id, prod_id, name):
    """Updates metadata for an existing email."""
    emails = load_emails()
    updated = False
    for e in emails:
        if e.get('address') == address:
            e['stage_id'] = stage_id
            e['prod_id'] = prod_id
            e['name'] = name
            updated = True
            break
            
    if not updated:
        return False
        
    try:
        with open(STORAGE_FILE, 'w') as f:
            json.dump({"emails": emails}, f, indent=4)
        return True
    except IOError:
        return False

def delete_email(address):
    """Removes an email address from storage."""
    emails = load_emails()
    new_list = [e for e in emails if e.get('address') != address]
    
    if len(new_list) == len(emails):
        return False # No change
        
    try:
        with open(STORAGE_FILE, 'w') as f:
            json.dump({"emails": new_list}, f, indent=4)
        return True
    except IOError:
        return False

def save_all_emails(emails_list):
    """Overwrites the storage with the provided list of emails."""
    try:
        with open(STORAGE_FILE, 'w') as f:
            json.dump({"emails": emails_list}, f, indent=4)
        return True
    except IOError as e:
        print(f"Error saving all emails: {e}")
        return False
