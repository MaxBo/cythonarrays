import sys
from typing import List
import numpy as np
from distutils.extension import Extension


if sys.platform == 'win32':
    extra_compile_args = ['/openmp']
    extra_link_args = None
else:
    # linux
    extra_compile_args = ['-fopenmp']
    extra_link_args = ['-fopenmp']

def make_ext(modname: str, sources: List[str], **kwargs) -> Extension:
    """
    Make Extension for module using the given sources
    uses the platform specific compile and link arguments to use openmp

    Parameters
    ----------
    modname:
        the name of the extension module to build
    sources:
        list of source filenames, relative to the distribution root
        (where the setup script lives), in Unix form (slash-separated)
        for portability
    """
    if not isinstance(sources, list):
        sources = [sources]
    extension = Extension(modname,
                          sources=sources,
                          extra_compile_args=extra_compile_args,
                          extra_link_args=extra_link_args,
                          include_dirs=[np.get_include()],
                          **kwargs,
                          )
    return extension
