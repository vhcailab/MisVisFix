import base64
import uuid
from django.core.files.base import ContentFile


def save_base64_image(base64_string, image_field, folder_name):
    """
    Saves a base64 image to the given ImageField under the specified folder.
    
    :param base64_string: The base64-encoded image string.
    :param image_field: The ImageField to save the file to.
    :param folder_name: The subfolder name (e.g. 'gpt' or 'claude').
    :return: The relative URL of the saved file.
    """
    # Handle optional data URL header
    if ';base64,' in base64_string:
        _, imgstr = base64_string.split(';base64,')
    else:
        imgstr = base64_string

    ext = 'png'  # Or infer type if you have multiple formats
    unique_id = uuid.uuid4().hex  # random unique id

    filename = f"{folder_name}_{unique_id}.{ext}"

    image_field.save(filename, ContentFile(base64.b64decode(imgstr)), save=True)

    return image_field.url
