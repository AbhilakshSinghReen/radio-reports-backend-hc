import os
import nibabel as nib
import numpy as np
import json
from skimage import measure
from radio_reports.settings import BASE_DIR

dummy_models_dir = os.path.join(BASE_DIR, "hc_data", "models")
dummy_models = {

}

segments_json_path = os.path.join(os.path.dirname(__file__), "segments.json")

segment_value_to_name = {}
segment_names = []
with open(segments_json_path, 'r') as file:
    data = json.load(file)
    segment_value_to_name = {int(key): value for key, value in data.items()}
    segment_names = [value for key, value in data.items()]

def get_polygonal_mesh_from_voxel_data(volume_data, voxel_spacing):
    verts, faces, normals, values = measure.marching_cubes(
        volume_data,
        level=None,
        spacing=voxel_spacing,
        step_size=1,
        allow_degenerate=False,
    )
    faces = faces + 1
    return verts, faces, normals, values

def write_obj_file(output_path, verts, faces, normals, values):
    with open(output_path, 'w') as obj_file:
        for item in verts:
            obj_file.write("v {0} {1} {2}\n".format(item[0],item[1],item[2]))

        for item in normals:
            obj_file.write("vn {0} {1} {2}\n".format(item[0],item[1],item[2]))

        for item in faces:
            obj_file.write("f {0}//{0} {1}//{1} {2}//{2}\n".format(item[0],item[1],item[2]))

def get_average_index_of_1_values(volume_data):
    val_1_indices = np.where(volume_data == 1)
    val_1_average_index = np.mean(val_1_indices, axis=1)
    return val_1_average_index.tolist()

def save_segment_as_object(output_file_path, _volume_data, voxel_spacing, segment_value):
   volume_data = _volume_data.copy()
   volume_data[volume_data != segment_value] = 0
   volume_data[volume_data == segment_value] = 1
   verts, faces, normals, values = get_polygonal_mesh_from_voxel_data(volume_data, voxel_spacing)

   ###
   # TODO (Dr. Amit): (verts, faces, normals, values) represent the mesh generated. We have to:
   # Remove excess polygons/triangles from this Mesh
   # Make the edges smoother to make it look better
   # Make the mesh watertight

   # After making changes to the mesh you can write the file using the function below if you have (verts, faces, normals) 
   # or you can write .obj using the library you used to edit the mesh.
   ###

   
   write_obj_file(output_file_path, verts, faces, normals, values)

   segment_geometric_origin = get_average_index_of_1_values(volume_data)
   return segment_geometric_origin

def total_segmentator_output_to_objs(ts_out_file_path, output_folder, segments_of_interest):
    segments_of_interest = set(segments_of_interest)

    nifti_image = nib.load(ts_out_file_path)
    voxel_spacing = nifti_image.header.get_zooms()
    volume_affine = nifti_image.affine
    volume_data = nifti_image.get_fdata()

    segment_values = np.unique(volume_data)
    output_metadata = {
        'input_volume': {
            'shape': volume_data.shape,
            'voxel_spacing': voxel_spacing,
            'affine': volume_affine,
        },
        'meshes': [],
    }
    # output_metadata_json_path = os.path.join(output_folder, f"metadata.json")
    # with open(output_metadata_json_path, 'w') as file:
    #     json.dump(output_metadata, file, indent=2)

    for segment_value in segment_values:
        if int(segment_value) == 0: # background
            continue

        segment_name = segment_value_to_name.get(int(segment_value), None)
        if segment_name is None:
            # print(f"No name found for segment value {segment_value}. Skipping this segment...")
            continue

        segment_obj_output_path = os.path.join(output_folder, f"{segment_name}.obj")
        segment_geometric_origin = save_segment_as_object(segment_obj_output_path, volume_data, voxel_spacing, segment_value)

        output_metadata['meshes'].append({
            'name': f"{segment_name}.obj",
            'geometricOrigin': json.dumps(segment_geometric_origin),
            'isROI': segment_name in segments_of_interest,
        })
        # with open(output_metadata_json_path, 'w') as file:
        #     json.dump(output_metadata, file, indent=2)

        # print(f"Saved segment {segment_name} as {segment_name}.obj")
    
    return output_metadata
