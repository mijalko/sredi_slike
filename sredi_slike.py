__author__ = 'mijalko'
import exifread
import enzyme
import datetime
import struct
import sys
from optparse import OptionParser

from hachoir_metadata import extractMetadata
from hachoir_parser import createParser
from os import walk
import os
import shutil

FOLDER_FORMAT = "%Y_%m_%d"

def get_fiels_and_folders(start_folder, destination=None, import_pictures = False):
    for (dirpath, dirnames, filenames) in walk(start_folder):
        for f in filenames:
            try:
                path = os.path.join(dirpath, f)
                fileName, fileExtension = os.path.splitext(path)
                if fileExtension.lower().strip() in (".jpg", ".avi"):

                    desired_folder_name = None
                    if fileExtension.lower().strip() == ".jpg":
                        with open(path, 'rb') as opened_file:
                            tags = exifread.process_file(opened_file)
                            if "Image DateTime" in tags:
                                creation_time = tags["Image DateTime"]
                                # 2015:01:01 01:16:56
                                date_object = datetime.datetime.strptime(creation_time.printable, '%Y:%m:%d %H:%M:%S')
                                creation_date = date_object

                                desired_folder_name = creation_date.strftime(FOLDER_FORMAT)
                            else:
                                print "warning: %s does not have creation time info" % path
                    else:
                        try:
                            parser = createParser(unicode(path))
                            mtd = extractMetadata(parser)
                            creation_date = mtd.get('creation_date')
                            desired_folder_name = creation_date.strftime(FOLDER_FORMAT)
                        except:
                            print "error parsing file " + path

                    if desired_folder_name is not None:
                        desired_folder = os.path.join(start_folder, desired_folder_name)

                        if desired_folder != dirpath or destination is not None:
                            if desired_folder != dirpath and not import_pictures:
                                print "file %s should be in %s" % (path, desired_folder)

                            if destination is None:
                                destination_file = os.path.join(desired_folder, f)
                            else:
                                desired_folder = os.path.join(destination, desired_folder_name)
                                destination_file = os.path.join(destination, desired_folder_name, f)

                            if not os.path.exists(desired_folder):
                                print "creating folder" + desired_folder
                                os.makedirs(desired_folder)
                            # copy path to destionation file
                            if destination is None:
                                # move file
                                if os.path.exists(destination_file):
                                    print "destination file " + destination_file + " exist. Move canceled"
                                else:
                                    shutil.move(path, destination_file)
                                    print "move %s to %s" % (path, destination_file)
                            else:
                                if os.path.exists(destination_file):
                                    print "destination file " + destination_file + " exist. Copy canceled"
                                else:
                                    shutil.copy(path, destination_file)
                                    print "copy %s to %s" % (path, destination_file)
                    else:
                        if destination is not None:
                            destination_file = os.path.join(destination, path[len(start_folder)+1:])
                            shutil.copy(path, destination_file)
                            print "copy %s to %s" % (path, destination_file)
            except Exception, e:
                print "Error parsing file " + f + " " + str(e)


def main():
    parser = OptionParser()
    parser.add_option("-i", "--import", dest="import_pic", action="store_true", default=False, help="import files from storage")

    source = raw_input("Enter pictures folder: ")
    destination = raw_input("Enter destination folder: ")

    if destination.strip() == "":
        destination = None

    (options, args) = parser.parse_args()
    if options.import_pic and destination is None:
        print "Error: You need to specify destination  folder"
        return

    get_fiels_and_folders(source, destination, options.import_pic)

if __name__ == '__main__':
    main()

