Set CURRENTDIR=%~dp0
Set CURRENTDRIVE==%~d0

cd %CURRENTDIR%\cythoninstallhelpers
python setup.py sdist bdist_wheel
cd %CURRENTDIR%\cythonarrays
python setup.py sdist bdist_wheel
cd %CURRENTDIR%\matrixconverters
python setup.py sdist bdist_wheel

cd %CURRENTDIR%
%CURRENTDRIVE%


