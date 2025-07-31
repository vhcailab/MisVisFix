import base64
import json

from ..constants.session_key import SESSION_KEY_HASH


def save_session(request, key, value):
    if key == 'corrected_gpt_image_code' or key == 'corrected_claude_image_code':
        encoded_code = base64.b64encode(value.encode('utf-8')).decode('utf-8')
        request.session[key] = encoded_code
    else:
        request.session[key] = value
    # request.session[key] = value
    request.session.modified = True  # Ensure session data is refreshed
    request.session.save()


def get_session(request, key):
    if key == 'corrected_gpt_image_code' or key == 'corrected_claude_image_code':
        encoded_code = request.session.get(key, None)
        if not encoded_code:
            return None
        return base64.b64decode(encoded_code).decode('utf-8')
    else:
        return request.session.get(key)
    # return request.session.get(key)


def save_encrypted_session(request, key, value):
    """
    Stores any kind of data in Django session securely using Base64 encoding.
    """
    try:
        # Convert value to JSON (Handles dict, list, int, float, string)
        json_str = json.dumps(value, default=str)  # Convert to string for storage
        encoded_value = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')  # Base64 encode
        request.session[key] = encoded_value  # Store in session
        request.session.modified = True  # Mark session as updated
    except Exception as e:
        print(f"Error saving session: {e}")


def get_decrypted_session(request, key):
    """
    Retrieves and decodes any kind of data from Django session.
    """
    try:
        encoded_value = request.session.get(key, None)  # Get stored value
        if not encoded_value:
            return None  # Handle missing session data safely

        decoded_bytes = base64.b64decode(encoded_value)  # Decode Base64
        decoded_json = json.loads(decoded_bytes.decode('utf-8'))  # Convert back to Python object

        return decoded_json
    except (base64.binascii.Error, json.JSONDecodeError, TypeError) as e:
        print(f"Error retrieving session: {e}")
        return None  # Return None if decoding fails
    

def store_hash_thread(request, key, data):
    hashes = get_decrypted_session(request, SESSION_KEY_HASH) or {}

    # Check if the key already exists
    if key in hashes:
        # Replace the existing data
        hashes[key] = data
    else:
        # Insert new data
        hashes[key] = data

    # Save updated chart analyses back to the session
    save_encrypted_session(request, SESSION_KEY_HASH, hashes)

def get_hash_data(request, hash):
    hashes = get_decrypted_session(request, SESSION_KEY_HASH) or None
    
    if hashes:
        if hash in hashes:
            return hashes[hash]
    return None
