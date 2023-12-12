from os import path
from shutil import move

from radio_reports.settings import CACHE_ROOT, MEDIA_ROOT


def upload_to_cloud_storage_from_cache(file_or_folder_name, upload_folder):
    try:
        move(path.join(CACHE_ROOT, file_or_folder_name), path.join(MEDIA_ROOT, upload_folder, file_or_folder_name))
    except Exception as e:
        print(e)
        return False
    
    return True
