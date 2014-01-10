import os
from tempfile import mkstemp, mkdtemp
from shutil import rmtree
from zipfile import ZipFile, ZIP_DEFLATED
from datetime import datetime
from boto.s3.connection import S3Connection
from boto.s3.key import Key

__version__ = "0.1.3"
__author__ = "Mark Embling"

class ZipBackup(object):

    """
    A compressed ZIP file backup. 

    Note: large inclusion operations can sometimes take time as files 
    are compressed on the fly. This prevents all the files being copied 
    to a temporary location (and using unnecessary extra space) and 
    storing up the need for a potentially large compression at the end.
    """

    def __init__(self, name):
        self.name = name
        _, self._path = mkstemp()
    
    def __enter__(self):
        return self
        
    def __exit__(self, type, value, traceback):
        self.close()
        
    def close(self):
        os.remove(self._path)
    
    def include_directory(self, path, preserve_paths=False, name=None):
        """Add the contents of a directory to the backup"""
        path = os.path.abspath(path)
        with ZipFile(self._path, 'a', ZIP_DEFLATED) as zipfile:
            for base,dirs,files in os.walk(path):
                for file in files:
                    filename = os.path.join(base, file)
                    try:
                        zipfile.write(filename,
                            self._get_filename_for_archive(
                                path, filename, preserve_paths, name))
                    except IOError:
                        pass
    
    def save_to_s3(self, bucket, access_key, secret_key):
        """Save the backup to Amazon S3"""
        conn = S3Connection(access_key, secret_key)
        bucket = conn.get_bucket(bucket)
        key = Key(bucket)
        key.key = '%s_%s.zip' % \
            (self.name, datetime.now().strftime("%Y%m%d%H%M%S"))
        key.set_contents_from_filename(self._path)

    def include_new_dir(self, name):
        """Add a new empty directory to the backup"""
        return BackupIncludedDirectory(name, self)
        
    def _get_filename_for_archive(self, directory, filename, 
                                  preserve_paths, name):
        if not preserve_paths:
            filename = filename.replace(directory, "")
        if name is not None:
            filename = name + os.sep + filename
        return filename
        
class BackupIncludedDirectory(object):

    """A new directory which is subsequently added to the backup"""

    def __init__(self, name, owner):
        self.name = name
        self.path = mkdtemp()
        self._owner = owner
    
    def __str__(self):
        return self.path
    
    def __enter__(self):
        return self
        
    def __exit__(self, type, value, traceback):
        self._owner.include_directory(self.path, preserve_paths=False, 
                                                 name=self.name)
        rmtree(self.path)
