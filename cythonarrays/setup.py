from setuptools import setup, find_namespace_packages
from cythoninstallhelpers.make_cython_extensions import make_extensions


ext_modnames = ['cythonarrays.array_shapes',
                'cythonarrays.tests.example_cython',
                'cythonarrays.tests.simple_cython',
                ]

package_name = "cythonarrays"

setup(
    #name=package_name,
    ext_modules=make_extensions(ext_modnames),
)