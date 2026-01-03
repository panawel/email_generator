import requests
import random
import string

BASE_URL = "https://api.mail.tm"

def get_domain():
    """Fetches a valid domain for account creation."""
    try:
        response = requests.get(f"{BASE_URL}/domains", timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get('hydra:member'):
            return data['hydra:member'][0]['domain']
        return None
    except requests.RequestException as e:
        print(f"Error getting domain: {e}")
        return None

# Word lists for meaningful names
ADJECTIVES = [
    "happy", "clever", "brave", "calm", "eager", "fancy", "gentle", "jolly", "kind", "lively",
    "nice", "proud", "silly", "witty", "zealous", "swift", "bright", "cool", "fiery", "lucky",
    "noble", "quiet", "royal", "super", "tiny", "wild", "young", "zesty", "epic", "rapid",
    "azure", "amber", "crimson", "golden", "indigo", "jade", "lemon", "lime", "navy", "olive",
    "teal", "violet", "white", "yellow", "rusty", "snowy", "sunny", "windy", "frosty", "misty"
]

ANIMALS = [
    "panda", "tiger", "lion", "eagle", "hawk", "wolf", "bear", "fox", "deer", "koala",
    "cat", "dog", "owl", "seal", "swan", "duck", "frog", "goat", "crab", "fish",
    "shark", "whale", "dolphin", "zebra", "camel", "llama", "moose", "mouse", "rat", "rabbit",
    "horse", "sheep", "cobra", "viper", "gecko", "iguana", "python", "turtle", "beetle", "butterfly",
    "spider", "falcon", "otter", "badger", "beaver", "bison", "dingo", "hyena", "jaguar", "lemur"
]

def generate_username():
    """Generates a meaningful username like 'happy-tiger-123'."""
    adj = random.choice(ADJECTIVES)
    noun = random.choice(ANIMALS)
    num = random.randint(100, 999)
    return f"{adj}-{noun}-{num}"

def create_account():
    """Creates a new random account and returns details (address, password, token)."""
    domain = get_domain()
    if not domain:
        return None
        
    # username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    username = generate_username()
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    address = f"{username}@{domain}"
    
    try:
        # Register
        reg_response = requests.post(f"{BASE_URL}/accounts", json={
            "address": address,
            "password": password
        }, timeout=10)
        reg_response.raise_for_status()
        
        # Get Token
        token = get_token(address, password)
        if token:
            return {
                "address": address,
                "password": password,
                "token": token
            }
        return None
    except requests.RequestException as e:
        print(f"Error creating account: {e}")
        return None

def get_token(address, password):
    """Obtains a Bearer token for an existing account."""
    try:
        response = requests.post(f"{BASE_URL}/token", json={
            "address": address,
            "password": password
        }, timeout=10)
        response.raise_for_status()
        return response.json().get('token')
    except requests.RequestException as e:
        print(f"Error getting token: {e}")
        return None

def get_messages(token):
    """Fetches list of messages using the Auth token."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/messages", headers=headers, timeout=10)
        response.raise_for_status()
        return response.json().get('hydra:member', [])
    except requests.RequestException as e:
        print(f"Error fetching messages: {e}")
        return []

def get_message_content(token, message_id):
    """Fetches full message content."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/messages/{message_id}", headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching message content: {e}")
        return None

def mark_message_as_seen(token, message_id):
    """Marks a message as seen/read."""
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/merge-patch+json"
        }
        data = {"seen": True}
        response = requests.patch(f"{BASE_URL}/messages/{message_id}", json=data, headers=headers, timeout=10)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"Error marking message as seen: {e}")
        return False
