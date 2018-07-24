# Also see https://pymotw.com/2/zipfile/ for how to use zipfile module

import logging
import sys
import os
from os import listdir, mkdir, chdir, rename, remove
os.environ["UNRAR_LIB_PATH"] = "/usr/lib/libunrar.so"
from unrar import rarfile

from os.path import isfile, join, isdir, splitext, basename, split
import re

import zipfile
from zipfile import ZipFile
try:
    import zlib
    compression = zipfile.ZIP_DEFLATED
except:
    compression = zipfile.ZIP_STORED

import string
import shutil
from titlecase import titlecase
from tempfile import mkdtemp

from collections import namedtuple
from itertools import groupby



def main(in_dir, out_dir):
    logging.basicConfig(format='%(levelname)s:%(message)s',
                        level=logging.DEBUG)

    chdir(in_dir)

    onlyfiles = [f for f in listdir(in_dir) if isfile(join(in_dir, f))]

    # Loop thru all ZIP files
    for filename in onlyfiles:
        # If not a ZIP file, skip file
        if not re.search("(.zip$)", filename.lower()):
            continue

        logging.info("Processing: {0}".format(filename))
        with ZipFile(join(in_dir, filename), 'r', zipfile.ZIP_DEFLATED) as myzip:
            zipOut = zipfile.ZipFile(join(out_dir, filename), 'w', zipfile.ZIP_DEFLATED)
            #infolist = myzip.infolist()
            namelist = myzip.namelist()
            for name in namelist:
                if re.search("(.epub$|.azw3$|.mobi$|.pdf$)", name.lower()):
                    myzip.extract(name, out_dir)
                else:
                    content = myzip.read(name)
                    zipOut.writestr(name, content, zipfile.ZIP_DEFLATED)
            zipOut.close()

    print("Done!")


if __name__ == '__main__':
    main("/mnt/hgfs/DDD", "/mnt/hgfs/DDD/output")
