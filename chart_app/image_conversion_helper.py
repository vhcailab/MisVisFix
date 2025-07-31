import requests
import base64
import httpx


def image_url_to_base64(url):
    try:
        image_data = base64.standard_b64encode(httpx.get(url).content).decode("utf-8")
        return image_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the image: {e}")
        return None


def get_image_type_from_url(url):
    response = requests.head(url)  # Fetch headers only
    content_type = response.headers.get('Content-Type')
    if content_type and content_type.startswith('image/'):
        return content_type.split('/')[-1]  # Return image type (e.g., 'png', 'jpeg')
    return None
