import sys
import numpy as np
from distutils.extension import Extension


if sys.platform == 'win32':
    extra_compile_args = ['/openmp']
    extra_link_args = None
else:
    # linux
    extra_compile_args = ['-fopenmp']
    extra_link_args = ['-fopenmp']

def make_ext(modname, sources, **kwargs):
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
