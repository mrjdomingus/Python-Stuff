# Also see https://pymotw.com/2/zipfile/ for how to use zipfile module

import logging, sys
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


class FileBase:
    # Order of extensions to keep in descending prererence
    ext_order = {'.zip': 0, '.pdf': 10, '.epub': 20, '.azw3': 30, '.mobi': 40 }
    
    def __init__(self, filename):
        self.filename = filename # We expect the full filename here.


    def process_file(self):
        pass

    def rename(self):
        bn = basename(self.filename)
        (bn, ext) = splitext(bn)
        (head, _) = split(self.filename)
        m = re.search(r"\W(\d+)(nd|rd|th)$",bn)
        if m:
            logging.debug("Match edition: {0}".format(m.string))
            (start, end) = m.span()
            length = (end - start)
            bn = bn[:start] + ", " + m.group(1) + m.group(2) + " Edition" + bn[start+length:]

        # Kludge to deal with zip files that have been processed earlier
        if True:
            bn = titlecase(bn.replace("-", " "))
        else:
            bn = titlecase(bn)

        self.filename = join(head,(bn + ext))
        logging.debug("New filename: {0}".format(self.filename))
        return(self.filename)

    @staticmethod
    def unduplicate(namelist):
        no_more_dups = []
        # Define namedtuple type
        Document = namedtuple('Document', ['basename', 'ext'])

        documents = []
        try:
            # Split each file name in a (root, ext) tuple
            for t in [(splitext(doc)) for doc in namelist]:
                # Convert tuple in dict (via intermediate list) and convert then into namedtuple of type Document
                documents.append(Document(**(dict(zip(['basename', 'ext'],list(t))))))
        except Exception as e: print(e)

        keyfunc = lambda doc: doc.basename

        documents = sorted(documents, key=keyfunc)

        doc_map = {}  
        # Use dict comprehensions to group all extensions by root part of file name
        try:
            doc_map = {
                key: [doc.ext for doc in group] 
                for key, group in groupby(documents, lambda doc: doc.basename)
            }
        except Exception as e: print(e)

        for key in doc_map.keys():
            if len(doc_map[key]) == 1:
                no_more_dups.append(key + doc_map[key][0] )
            else:
                extfunc = lambda ext: FileBase.ext_order.get(ext, 999)
                extensions = sorted(doc_map[key], key=extfunc)
                for ext in extensions:
                    if ext == '.zip':
                        no_more_dups.append(key + ext )
                    else:
                        no_more_dups.append(key + ext )
                        break
        
        return no_more_dups

class RAR_or_ZIPFile(FileBase):
    def __init__(self, filename, out_dir):
        super().__init__(filename)
        (_, ext) =splitext(self.filename)
        if ext.lower() == ".rar":
            self.__rar_or_zip = rarfile.RarFile(filename)
        elif ext.lower() == ".zip":
            self.__rar_or_zip = zipfile.ZipFile(filename)
        else:
            logging.error("Unsupported type of compressed file: {0}!".format(ext))
        self.__out_dir = out_dir


    def process_file(self):
        super().process_file()
        
        TMPDIR = mkdtemp()
        chdir(TMPDIR)

        namelist = self.__rar_or_zip.namelist()

        namelist = FileBase.unduplicate(namelist)

        # First empty TMPDIR        
        files_to_clean = [f for f in listdir(TMPDIR) if isfile(join(TMPDIR, f))]
        for f in files_to_clean:
            remove(join(TMPDIR,f))

        # Extract files from unduplicated list
        for name in namelist:
            self.__rar_or_zip.extract(name, TMPDIR)
        
        extracted_files = [f for f in listdir(TMPDIR) if isfile(join(TMPDIR, f))]

        # Below code assumes that temporary, extracted files are located in current directory
        for tmpfile in extracted_files:
            # Improve file name
            rename(tmpfile, FileBase(join(TMPDIR,tmpfile)).rename())

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
            # Kludge to deal with zip files that have been processed earlier
            if False:
                zipname = join(self.__out_dir,  titlecase(splitext(basename(self.filename))[0].replace("-", " ")) + ".zip")
            else:
                zipname = join(self.__out_dir,  titlecase(splitext(basename(self.filename))[0]) + ".zip")
            try:
                with ZipFile(zipname, 'w') as myzip:
                    try:
                        for tmpfile in extracted_files:
                            myzip.write(tmpfile, compress_type=compression)
                    finally:
                        myzip.close()
                        rename(zipname, FileBase(zipname).rename())
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
        if not re.search("(.rar$|.zip$)", filename.lower()):
            continue

        logging.info("Processing: {0}".format(filename))
        rar = RAR_or_ZIPFile(join(in_dir, filename), out_dir)
        rar.process_file()
    
    print("Done!")

if __name__ == '__main__':
   main("/mnt/hgfs/DDD", "/mnt/hgfs/DDD/output")

