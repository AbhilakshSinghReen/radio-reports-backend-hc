from shutil import copy2
import os
from radio_reports.settings import BASE_DIR

sh_script_path = os.path.join(os.path.dirname(__file__), "run_total_segmentator.sh")
sh_script_nii_image_path = os.path.join(os.path.dirname(__file__), "vol.nii.gz")
sh_script_out_path = os.path.join(os.path.dirname(__file__), "seg.nii.gz")

dummy_seg = "D:/Programming/Hackathons/Pragati/Stage 3/segmenting/1-tsoc.nii.gz"
dummy_segs_dir = os.path.join(BASE_DIR, "hc_data", "segmentations")
dummy_segs = {
    'navneet_chest.nii.gz': "10-tsoc.nii.gz",
    '106606287_chestabd.nii.gz': "7-tsoc.nii.gz",
    '106467972_chestabd.nii.gz': "5-tsoc.nii.gz",
    '106641577_chest_abd.nii.gz': "8-tsoc.nii.gz",
    '106467972_chestabd_cropped.nii.gz': "6-tsoc.nii.gz",
    '106466155_chest.nii.gz': "3-tsoc.nii.gz",
    '106272387_chest_cropped.nii.gz': "1-tsoc.nii.gz",
    '106641577_chestcropped.nii.gz': "9-tsoc.nii.gz",
    '106466155_neck.nii.gz': "4-tsoc.nii.gz",
    '106272387_neck.nii.gz': "2-tsoc.nii.gz",
}

def run_total_segmentator_on_nii_image(nii_image_path, ts_out_file_path, nifti_file_name):
    copy2(os.path.join(dummy_segs_dir, dummy_segs[nifti_file_name]), ts_out_file_path)
