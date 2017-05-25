Set CURRENTDIR=%~dp0
Set CURRENTDRIVE==%~d0

cd %CURRENTDIR%\docs_rst
call make.bat clear
call make.bat html

cd %CURRENTDIR%
%CURRENTDRIVE%


