#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 21 17:39:38 2022

@author: dmitriy_mikhailov

This script generate slice-timig values assuming interrevealed order of slice
accuisiance with zero slice delay and using information about TR and number of slice 
extracted from .nii fMRI functional files and .json BIDS sidecards.

This script obtain json pathes from stdin.
"""


import os
import sys
import json
from re import match
from re import sub
import nibabel as nib
import json

json_pattern_string = "r'.*task-rest_bold\.json'"

bids_dir = os.getcwd()
bids_dir = os.path.join(bids_dir, 'test')

subject_list=[]





def get_functional_BIDSSidecards(bids_dir: str):
    """ 
    This function take all json functional bids-sidecards 
    using absolute path bids_dir
    """

    root, dirs, files = next(os.walk(bids_dir))
    sub_dirs = [x for x in dirs if match(r'sub', x)]

    full_target_json_files = []
    for sub_dir in sub_dirs:
        full_sub_dir = os.path.join(root, sub_dir)
        sub_root, sub_dirs, files = next(os.walk(full_sub_dir))
        for ses_dir in sub_dirs:
            full_ses_dir = os.path.join(sub_root, ses_dir)
            full_target_dir = os.path.join(full_ses_dir, 'func')
            
            target_root, target_dirs, target_files = next(os.walk(full_target_dir))
            target_json_files = [os.path.join(full_target_dir, x) for x in target_files if match(r'.*json', x)]
            
            full_target_json_files.append(target_json_files)
            
    return [item for sublist in full_target_json_files for item in sublist]

def make_slice_timing_values(TR=3, nSlice=41):
    order = list(range(0, nSlice, 2)) + list(range(1, nSlice, 2)) if (nSlice % 2) \
        else list(range(1, nSlice, 2)) + list(range(0, nSlice, 2))
    
    time_for_slice = TR / nSlice
    slice_timing = [order.index(pos)*time_for_slice for pos in list(range(0, nSlice, 1))]
    
    return slice_timing
        
def get_slice_timing_parameters(json_path: str):
    """ This function using bids structure of directory where BIDS_json 
    situated find .nii data and extract TR (in msec) and number of slice from it
    """
    nii_path = sub('.json', '.nii.gz', json_path)
    nii_data = nib.load(nii_path)
    return (nii_data.header.get_zooms()[3], nii_data.shape[2])

def write_slice_timing_to_json(json_path: str, slice_timing_vals: tuple): 
    with open(json_path, 'r+') as json_file:
        json_data = json.load(json_file)
        json_data['SliceTiming'] = slice_timing_vals
        json_file.seek(0)
        json_file.truncate(0)
        json.dump(json_data, json_file, indent=4)

def check_TR_coinsidance(json_path: str, TR_from_data: float):
    with open(json_path, 'r') as json_file:
        json_data = json.load(json_file)
    
    TR_from_sidecard = json_data['RepetitionTime']
        
    if TR_from_sidecard != TR_from_data:
        msg = """Extracted from .nii.gz file RepetitionTime 
                doesn't coinside with the RepetitionTime from json BIDS sidecards.
                File: {0}
                TR from .json: {1}
                TR from .nii.gz: {2}""".format(json_path, TR_from_sidecard, TR_from_data)
        raise ValueError(msg)
    
def main(args):
    json_pathes = args
    there_were_errors = False
    all_parameters = []
    print("Working with files: " + str(json_pathes))
    print("Checking files...")
    for json_path in json_pathes:
        
        if not os.path.isfile(json_path):
            raise FileNotFoundError(json_path)
            
        slice_timing_parameters = get_slice_timing_parameters(json_path)
        try:
            check_TR_coinsidance(json_path, slice_timing_parameters[0])
        except Exception as err:
            print("Error: " + str(err))
            there_were_errors = True
        else:
            all_parameters.append((json_path, slice_timing_parameters))
    
    if there_were_errors:
        msg = 'We have problems in some files. Processing is aborted, look messages above.'
        raise ValueError(msg)
    else:
        print("Complete!")
        print("Start adding slice-timing values.")
        for json_path, slice_timing_parameters in all_parameters:
            print("File: " + json_path)
            slice_timing_vals = make_slice_timing_values(*slice_timing_parameters)
            print("Slice-timing: " + str(slice_timing_vals))
            write_slice_timing_to_json(json_path, slice_timing_vals)
            print("Saved!")
    print("Slice-timing added to {} files!".format(len(all_parameters)))
            
if __name__ == '__main__':
    sys.argv.pop(0)
    main(sys.argv)
