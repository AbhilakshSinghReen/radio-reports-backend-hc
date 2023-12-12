import os
import json


from radio_reports_api.cloud_storage import (
    upload_to_cloud_storage_from_cache,
)
from radio_reports_api.cache import (
    create_folder_in_cache,
    clean_cache_for_report_media_id
)
from radio_reports.settings import CACHE_ROOT
from radio_reports_api.task_scripts.nifti_to_segmentation import run_total_segmentator_on_nii_image
from radio_reports_api.task_scripts.segmentation_to_mesh import total_segmentator_output_to_gltf
from radio_reports_api.utils import unique_str
from radio_reports_api.models import Report


# get_simplified_report = ",,,"
# get_segments_of_interest = "wdq"

default_report_simplification_languages = ["english", "hindi"]

def generate_report_text_and_model(
        report_id,
        report_media_id,
        cached_nii_file_name,
        report_data,
        nifti_file_name
    ):
    try:
        report_object = Report.objects.get(id=report_id)
    except:
        task_status = f"Report with id {report_id} not found"
        print(task_status)
        return task_status
    
    nii_file_path = os.path.join(CACHE_ROOT, cached_nii_file_name)
    ts_out_file_path = os.path.join(CACHE_ROOT, f"{report_media_id}-segmented.nii.gz")
    meshes_output_dir_path = create_folder_in_cache(report_media_id)
    
    report_object.processing_status = "Starting Task..."
    report_object.save()

    simplified_reports = {}

    # for language in default_report_simplification_languages:
    #     try:
    #         simplified_reports[language] = get_simplified_report(report_data, language)
    #     except:
    #         task_status = f"Failed at report simplification for language: {language}."
    #         report_object.processing_status = task_status
    #         report_object.save()
    #         print(task_status)
    #         return task_status
        
    report_object.meshes_metadata = json.dumps(simplified_reports)
    report_object.processing_status = "Getting segments of interest..."
    report_object.save()

    try:
        # segments_of_interest = get_segments_of_interest(report_data)
        segments_of_interest = [
            'rib_left_10',
            'spleen',
            'foo_bar_that_does_not_exist',
            'adrenal_gland_left',
        ]
    except:
        task_status = f"Failed to get segments of interest."
        report_object.processing_status = task_status
        report_object.save()
        print(task_status)
        return task_status
    
    report_object.processing_status = "Running Total Segmentator on nii image..."
    report_object.save()

    try:
        run_total_segmentator_on_nii_image(nii_file_path, ts_out_file_path, nifti_file_name)
    except:
        task_status = f"Failed to run Total Segmentator on nii image."
        report_object.processing_status = task_status
        report_object.save()
        print(task_status)
        return task_status
    
    report_object.processing_status = "Generating glTF from segmentation..."
    report_object.save()

    # try:
    meshes_metadata = total_segmentator_output_to_gltf(ts_out_file_path, meshes_output_dir_path, nifti_file_name)
    # print(meshes_metadata)
    meshes_metadata['segmentsOfInterest'] = segments_of_interest
    # except:
    #     task_status = f"Failed to generate glTF from segmentation."
    #     report_object.processing_status = task_status
    #     report_object.save()
    #     print(task_status)
    #     return task_status

    
    
    report_object.processing_status = "Uploading glTF to Cloud Storage..."
    report_object.save()

    try:
        upload_to_cloud_storage_from_cache(report_media_id, "segment-meshes")
    except:
        task_status = f"Failed to upload glTF to Cloud Storage."
        report_object.processing_status = task_status
        report_object.save()
        print(task_status)
        return task_status
    
    report_object.meshes_metadata = json.dumps(meshes_metadata)
    report_object.save()

    report_object.processing_status = "Cleaning cache for report media id."
    report_object.save()

    try:
        clean_cache_for_report_media_id(report_media_id)
    except:
        task_status = f"Failed to clean cache for report media id."
        report_object.processing_status = task_status
        report_object.save()
        print(task_status)
        return task_status

    report_object.processing_status = "Processing completed."
    report_object.save()
