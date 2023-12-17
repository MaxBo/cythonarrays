import re
import os

def get_version(package_name: str,
                setupfilepath: str,
                package_dir:str = 'src',
                versionfile:str ='_version.py') -> str:
    """
    Parse the version number from a version file

    Parameters
    ----------
    package_name:
        the name of the package the version is searched for
    setupfilepath:
        the filepath, where the setupfile can be found
    package_dir:
        the subdirectory with the source code of the version file
    versionfile:
        the filename of the python module with the version number
    """
    folder = os.path.join(os.path.dirname(setupfilepath), package_dir)
    version_path= os.path.join(folder, package_name, versionfile)
    try:
        verstrline = open(version_path, "rt").read()
    except IOError:
        raise IOError('Version file {} not found'.format(version_path))
    VSRE = r"^[_]{0,2}version[_]{0,2}\s*=\s*['\"]([^'\"]*)['\"]"
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        verstr = mo.group(1)
    else:
        raise RuntimeError(
            "Unable to find version string in {}.".format(version_path,))
    return verstr