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
        self.filename = filename


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
        for idx, name in enumerate(namelist):
            if re.search(".zip$", name.lower()):
                zipIndex = idx
                logging.debug(">>>zipfile: {0}".format(namelist[zipIndex]))
            if re.search(".pdf$", name.lower()):
                pdfIndex = idx
                logging.debug(">>>pdffile: {0}".format(namelist[pdfIndex]))
            if re.search(".epub$", name.lower()):
                epubIndex = idx
                logging.debug(">>>epubfile: {0}".format(namelist[epubIndex]))
            if re.search(".azw3$", name.lower()):
                azw3Index = idx
                logging.debug(">>>azw3file: {0}".format(namelist[azw3Index]))
            if re.search(".mobi$", name.lower()):
                mobiIndex = idx
                logging.debug(">>>mobifile: {0}".format(namelist[mobiIndex]))

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
        
        # Create zip file
        zipname = join(self.__out_dir,  titlecase(splitext(basename(self.filename))[0].replace("-", " ")) + ".zip")
        try:
            with ZipFile(zipname, 'w') as myzip:
                files_to_zip = [f for f in listdir(TMPDIR) if isfile(join(TMPDIR, f))]
                try:
                    for tmpfile in files_to_zip:
                        if tmpfile == basename(zipname):
                            continue
                        nameparts = splitext(tmpfile)
                        newfilename = titlecase(nameparts[0].replace("-", " ")) + nameparts[1]
                        rename(tmpfile, newfilename)
                        myzip.write(newfilename, compress_type=compression)
                finally:
                    myzip.close()
                    # Move zip file out of the way, before next cleanup
                    #shutil.move(zipname, self.__out_dir)
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

