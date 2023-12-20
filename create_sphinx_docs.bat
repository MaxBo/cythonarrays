
Set CURRENTDIR=%~dp0
Set CURRENTDRIVE==%~d0

cd %CURRENTDIR%cythoninstallhelpers
cd %CURRENTDIR%cythonarrays

SET SC=%CURRENTDIR%cythoninstallhelpers\src\cythoninstallhelpers
sphinx-apidoc -f --separate -o %CURRENTDIR%docs_rst\cythoninstallhelpers %SC% %SC%\tests
SET SC=%CURRENTDIR%cythonarrays\src\cythonarrays
sphinx-apidoc -f --separate -o %CURRENTDIR%docs_rst\cythonarrays %SC% %SC%\tests

cd %CURRENTDIR%
%CURRENTDRIVE%

