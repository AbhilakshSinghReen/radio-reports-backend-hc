from shutil import copy2
import os
import nibabel as nib
import numpy as np
import json
import platform
import subprocess

from radio_reports.settings import SLICER_EXE_PATH, BASE_DIR

dummy_models_dir = os.path.join(BASE_DIR, "hc_data", "models")
dummy_models = {
    'navneet_chest.nii.gz': "10.gltf",
    '106606287_chestabd.nii.gz': "7.gltf",
    '106467972_chestabd.nii.gz': "5.gltf",
    '106641577_chest_abd.nii.gz': "8.gltf",
    '106467972_chestabd_cropped.nii.gz': "6.gltf",
    '106466155_chest.nii.gz': "3.gltf",
    '106272387_chest_cropped.nii.gz': "1.gltf",
    '106641577_chestcropped.nii.gz': "9.gltf",
    '106466155_neck.nii.gz': "4.gltf",
    '106272387_neck.nii.gz': "2.gltf",
}

convertor_script_path = os.path.join(os.path.dirname(__file__), "seg_to_mesh.py")
convertor_script_input_path = os.path.join(os.path.dirname(__file__), "seg.nii.gz")
convertor_script_out_path = os.path.join(os.path.dirname(__file__), "model.gltf")

current_os = platform.system()
if current_os == "Windows":
    run_convertor_script_cmd_args = [
        SLICER_EXE_PATH,
        "--python-script",
        convertor_script_path,
        "--no-splash",
        "--no-main-window",
    ]
else:
    run_convertor_script_cmd_args = [
        SLICER_EXE_PATH,
        "--no-splash",
        "--no-main-window",
        "--python-script",
        convertor_script_path,
    ]

segments_json_path = os.path.join(os.path.dirname(__file__), "segments.json")

segment_value_to_name = {}
segment_names = []
with open(segments_json_path, 'r') as file:
    data = json.load(file)
    segment_value_to_name = {int(key): value for key, value in data.items()}
    segment_names = [value for key, value in data.items()]

def get_average_indices_of_all_values(volume_data):
    value_indices_sum = {}
    for i in range(volume_data.shape[0]):
        for j in range(volume_data.shape[1]):
            for k in range(volume_data.shape[2]):
                value = volume_data[i, j, k]

                if not value in value_indices_sum:
                    value_indices_sum[value] = {
                        'sumI': 0,
                        'sumJ': 0,
                        'sumK': 0,
                        'count': 0,
                    }
                
                value_indices_sum[value]['sumI'] += i
                value_indices_sum[value]['sumJ'] += j
                value_indices_sum[value]['sumK'] += k
                value_indices_sum[value]['count'] += 1

    value_average_indices = {}
    for value in value_indices_sum:
        value_average_indices[value] = [
            value_indices_sum[value]['sumI'] / value_indices_sum[value]['count'],
            value_indices_sum[value]['sumJ'] / value_indices_sum[value]['count'],
            value_indices_sum[value]['sumK'] / value_indices_sum[value]['count'],
        ]
    
    return value_average_indices

def get_output_metadata(ts_out_file_path):
    nifti_image = nib.load(ts_out_file_path)
    voxel_spacing = nifti_image.header.get_zooms()
    volume_affine = nifti_image.affine
    volume_data = nifti_image.get_fdata()

    output_metadata = {
        'input_volume': {
            'shape': volume_data.shape,
            # 'voxel_spacing': voxel_spacing,
            # 'affine': volume_affine.tolist(),
        },
        'meshes': [],
    }

    value_average_indices = get_average_indices_of_all_values(volume_data)
    for segment_value in value_average_indices:
        segment_name = segment_value_to_name.get(int(segment_value), None)
        if int(segment_value) == 0 or segment_name is None:
            continue

        output_metadata['meshes'].append({
            'name': f"{segment_name}",
            'geometricOrigin': json.dumps(value_average_indices[segment_value]),
        })
        # Get volume bounds shape also
        
    return output_metadata

def total_segmentator_output_to_gltf(ts_out_file_path, model_out_dir, nifti_file_name):
    model_out_path = os.path.join(model_out_dir, "model.gltf")
    copy2(os.path.join(dummy_models_dir, dummy_models[nifti_file_name]), model_out_path)
    # copy2(ts_out_file_path, convertor_script_input_path)
    # subprocess.run(run_convertor_script_cmd_args)
    # copy2(convertor_script_out_path, model_out_path)``
    
    output_metadata = get_output_metadata(ts_out_file_path)
    return output_metadata
