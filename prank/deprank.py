#!/usr/bin/python
import os

def deprank():
    current_dir = os.getcwd()
    images_dir = "/Users/manuelaguilar/Documents/udacity/prank/prank"

    os.chdir(images_dir)
    file_names = os.listdir(images_dir)
    
    for file_name in file_names:
        print "Renaming :"+file_name
        os.rename(file_name, file_name.translate(None,"0123456789"))

    os.chdir(current_dir)

deprank()

