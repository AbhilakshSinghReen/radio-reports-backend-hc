from uuid import uuid4
from time import time
from os import path
import random


def unique_str():
    return f"{uuid4()}--{round(time() * 1000)}"

def get_extension(file_path):
    split_file_name = path.basename(file_path).split('.')
    file_extension = ".".join(split_file_name[1:])
    return file_extension

def select_random_segment_names(segment_names, min_selected_count=2, max_selected_count=5):
    min_selected_count = max(0, min_selected_count)
    max_selected_count = min(len(segment_names), max_selected_count)

    if min_selected_count > max_selected_count:
        return []
    
    to_select_count = random.randint(min_selected_count, max_selected_count)
    selected_segment_names = random.sample(segment_names, to_select_count)
    return selected_segment_names
