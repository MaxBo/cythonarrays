SET CONDAENV=%1
IF "%CONDAENV%"=="" (
    SET CONDAENV=cythonarrays
    )
call conda create -y -n %CONDAENV% python=3.5 
call activate %CONDAENV%
call conda install -y numpy pandas cython xarray netCDF4 bottleneck
call conda install -y pytest

call cd cythoninstallhelpers
call python setup.py bdist_wheel
call python setup.py install
call cd ..
call cd cythonarrays
call python setup.py bdist_wheel
call python setup.py install
call cd ..
call cd matrixconverters
call python setup.py bdist_wheel
call python setup.py develop
call cd ..
