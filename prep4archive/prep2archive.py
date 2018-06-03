# Also see https://pymotw.com/2/zipfile/ for how to use zipfile module

import logging, sys
import os
from os import listdir, mkdir, chdir, rename, remove  
os.environ["UNRAR_LIB_PATH"] = "/usr/lib/libunrar.so"
from unrar import rarfile

from os.path import isfile, join, isdir, splitext, basename
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

class FileBase:
    def __init__(self, filename):
        self.filename = filename # We expect the full filename here.


    def process_file(self):
        pass


class RARFile(FileBase):
    def __init__(self, filename, out_dir):
        super().__init__(filename)
        self.__rar = rarfile.RarFile(filename)
        self.__out_dir = out_dir


    def process_file(self):
        super().process_file()
        
        TMPDIR = mkdtemp()
        chdir(TMPDIR)

        namelist = self.__rar.namelist()

        zipIndex, pdfIndex, epubIndex, azw3Index, mobiIndex = [-1] * 5
        # Warning, below for loop assumes that each specific file extension occurs only ONCE in the container file!
        for idx, name in enumerate(namelist):
            if re.search(".zip$", name.lower()):
                zipIndex = idx
                logging.debug(">>>zip-file: {0}".format(name))
            elif re.search(".pdf$", name.lower()):
                pdfIndex = idx
                logging.debug(">>>pdf-file: {0}".format(name))
            elif re.search(".epub$", name.lower()):
                epubIndex = idx
                logging.debug(">>>epub-file: {0}".format(name))
            elif re.search(".azw3$", name.lower()):
                azw3Index = idx
                logging.debug(">>>azw3-file: {0}".format(name))
            elif re.search(".mobi$", name.lower()):
                mobiIndex = idx
                logging.debug(">>>mobi-file: {0}".format(name))
            else:
                logging.warning(">>>unexptected file: {0}".format(name))

        # First empty TMPDIR        
        files_to_clean = [f for f in listdir(TMPDIR) if isfile(join(TMPDIR, f))]
        for f in files_to_clean:
            remove(join(TMPDIR,f))

        # Save the zip file in any case
        if zipIndex > -1:
            self.__rar.extract(namelist[zipIndex], TMPDIR)

        if pdfIndex > -1:
            self.__rar.extract(namelist[pdfIndex], TMPDIR)
        elif epubIndex > -1:
            self.__rar.extract(namelist[epubIndex], TMPDIR)
        elif azw3Index > -1:
            self.__rar.extract(namelist[azw3Index], TMPDIR)
        elif mobiIndex > -1:
            self.__rar.extract(namelist[mobiIndex], TMPDIR)
        
        extracted_files = [f for f in listdir(TMPDIR) if isfile(join(TMPDIR, f))]

        # Below code assumes that temporary, extracted files are located in current directory
        for tmpfile in extracted_files:
            nameparts = splitext(tmpfile)
            newfilename = titlecase(nameparts[0].replace("-", " ")) + nameparts[1]
            rename(tmpfile, newfilename)
        # Reacquire list of files
        extracted_files = [f for f in listdir(TMPDIR) if isfile(join(TMPDIR, f))]

        if len(extracted_files) == 0:
            # Do nothing
            pass
        elif len(extracted_files) == 1:
            # Copy the single file to the output dir
            shutil.move(extracted_files[0], self.__out_dir)
        else:
            # Create zip file
            zipname = join(self.__out_dir,  titlecase(splitext(basename(self.filename))[0].replace("-", " ")) + ".zip")
            try:
                with ZipFile(zipname, 'w') as myzip:
                    try:
                        for tmpfile in extracted_files:
                            myzip.write(tmpfile, compress_type=compression)
                    finally:
                        myzip.close()
            except Exception as e: print(e)

        # Delete temp directory
        shutil.rmtree(TMPDIR)


def main(in_dir, out_dir):
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    chdir(in_dir)

    onlyfiles = [f for f in listdir(in_dir) if isfile(join(in_dir, f))]

    # Loop thru all RAR files
    for filename in onlyfiles:
        # If not a RAR file, skip file
        if not re.search(".rar$", filename.lower()):
            continue

        logging.info("Processing: {0}".format(filename))
        rar = RARFile(join(in_dir, filename), out_dir)
        rar.process_file()
    
    print("Done!")

if __name__ == '__main__':
   main("/mnt/hgfs/DDD", "/mnt/hgfs/DDD/output")

