# -*- coding: utf-8 -*-

import os
import sys
import numpy as np
from Cython.Build import cythonize

from .build_config import (extra_compile_args,
                          extra_link_args,
                          make_ext,)


def make_extensions(ext_modnames, further_args={}, source_dir='src'):
    """
    add sources to the ext_modules specified in the input list

    Parameters
    ----------
    ext_modnames : list of str
        the extension modules to create
    further_args : dict with further arguments for extension module
    source_dir : str, optional (default='src')
        the source directory relative to the setup.py file

    Returns
    -------
    extensions : list of Extension-instances
    """
    extensions = []


    suffix = '.pyx'
    for modname in ext_modnames:
        mn = modname.split('.')
        pyxfilename = os.path.join(source_dir, *mn) + suffix
        sources = [pyxfilename]
        further_arg = further_args.get(modname, {})
        if further_arg:
            more_sources = further_arg.pop('sources')
            ms = mn[:-1]
            full_more_sources = []
            for source in more_sources:
                full_source = [source_dir] + ms + [source]
                full_more_sources.append(os.sep.join(full_source))
            sources.extend(full_more_sources)
        extension = make_ext(modname, sources, **further_arg)
        extensions.append(extension)

    cython_extensions = cythonize(extensions,
                                  annotate=True,
                                  compiler_directives={'linetrace': True,},
                                  )
    return cython_extensions