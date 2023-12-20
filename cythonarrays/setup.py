from pathlib import Path
import sys
src = Path(__file__).parent.joinpath('src')
sys.path.append(str(src))

from setuptools import setup
from cythonarrays.make_cython_extensions import make_extensions


ext_modnames = ['cythonarrays.array_shapes',
                'cythonarrays.tests.example_cython',
                'cythonarrays.tests.simple_cython',
                ]

package_name = "cythonarrays"

setup(
    ext_modules=make_extensions(ext_modnames),
)