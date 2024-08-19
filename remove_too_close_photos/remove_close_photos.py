#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, math
from lib.exif_read import ExifRead as EXIF
from lib.geo import gps_distance

TRASH_DIRECTORY = "/home/nlehuby/mapping/zz_photos_nulles/trop_proche/"

def list_images(directory):
    ''' 
    Create a list of image tuples sorted by capture timestamp.
    @param directory: directory with JPEG files 
    @return: a list of image tuples with time, directory, lat,long...
    '''
    file_list = []
    for root, sub_folders, files in os.walk(directory):
        file_list += [os.path.join(root, filename) for filename in files if filename.lower().endswith(".jpg")]

    files = []
    for filepath in file_list:
        metadata = EXIF(filepath)
        try:
            t = metadata.extract_capture_time()
            geo = metadata.extract_geo()
            files.append((filepath, t, geo["latitude"], geo["longitude"]))
        except KeyError:
            print("Photo {} ignorée (exif manquants)".format(filepath))

    files.sort(key=lambda timestamp: timestamp[1])
    return files

def main(path):
    images_list=list_images(path)
    print("(rappel : le dossier poubelle est {} )".format(TRASH_DIRECTORY))

    for i,pic in enumerate(images_list):
        if i == 0 :
            continue
        current_geo = (images_list[i][2],images_list[i][3])
        last_geo = (images_list[i-1][2],images_list[i-1][3])
        distance = gps_distance(current_geo,last_geo)
        if distance < 1:
            current_picture_filepath = images_list[i][0]
            file_name = current_picture_filepath.split('/')[-1]
            os.rename(current_picture_filepath, "{}{}".format(TRASH_DIRECTORY,file_name))
            print("> Déplacement de la photo {} vers le dossier poubelle".format(file_name))
              

if __name__ == '__main__':
    
    path = sys.argv[1]
    main(path)
	

