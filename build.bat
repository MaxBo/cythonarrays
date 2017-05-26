Set CURRENTDIR=%~dp0
Set CURRENTDRIVE==%~d0

cd %CURRENTDIR%\cythoninstallhelpers
python setup.py sdist bdist_wheel
REM gpg --detach-sign -a dist/package-1.0.1.tar.gz
REM gpg --detach-sign -a dist/package-wheel
REM twine upload package-0.5.2-py3-none-any.whl package-0.5.2-py3-none-any.whl.asc
REM twine upload package-1.0.1.tar.gz package-1.0.1.tar.gz.asc
cd %CURRENTDIR%\cythonarrays
python setup.py sdist bdist_wheel upload --sign
cd %CURRENTDIR%\matrixconverters
python setup.py sdist bdist_wheel

cd %CURRENTDIR%
%CURRENTDRIVE%


