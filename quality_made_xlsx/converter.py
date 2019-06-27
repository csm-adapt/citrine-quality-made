from pypif import pif
from quality_made_xlsx.read_excel import read_excel
from quality_made_xlsx.process_archive import process_archive


def convert(files=[]):
    """
    Convert files into a pif

    :param files: to convert
    :param important_argument: an important argument, must be provided
    :param whatever_argument: a less important argument with default 1
    :param do_some_extra_thing:
    :param kwargs: any other arguments
    :return: the pif produced by this conversion
    """
    return read_excel(files[0])

if __name__ == '__main__':
    import sys
    with open(sys.argv[1].replace('.xlsx', '-pif.json'), 'w') as ofs:
        pif.dump(convert(files=[sys.argv[1]]), ofs, indent=4)
