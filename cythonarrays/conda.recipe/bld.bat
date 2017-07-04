xcopy /e /Y "%RECIPE_DIR%\.." "%SRC_DIR%"
"%PYTHON%" setup.py sdist bdist_wheel install
if errorlevel 1 exit 1