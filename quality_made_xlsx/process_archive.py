from tarfile import TarFile
from zipfile import ZipFile
import os


def process_archive(archive):
    """
    Entry point for processing an archive. The type of archive
    is recognized from the archive file extension.

    :param archive: Archive to process.
    :type archive: str
    :return: TBW
    """
    basename, ext = os.path.splitext(archive)
    return {
        '.tgz': lambda fname: process_tar(fname, compression='gzip'),
        '.bz2': lambda fname: process_tar(fname, compression='bzip2'),
        '.tar': lambda fname: process_tar(fname),
        '.xz': lambda fname: process_tar(fname, compression='xz'),
        '.zip': lambda fname: process_zip(fname)
    }[ext](archive)


def process_tar(archive, compression=None):
    """
    Unpacks a .tar archive, including those compressed using
    gzip, bz2, or lzma.

    :param archive: The name of the .tar archive.
    :type archive: str
    :param compression: Whether the archive is compressed. Recognized
        values: gzip, bzip2, xz, lzma, or None
    :type compression: str or None
    :return: TBW
    """
    pass


def process_zip(archive):
    """
    Unpack the .zip file into the current dataset.

    :param archive: The name of the .zip archive.
    :type archive: str
    :return: TBW
    """
    pass


