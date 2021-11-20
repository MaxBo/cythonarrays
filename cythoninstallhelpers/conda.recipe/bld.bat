xcopy /e /Y "%RECIPE_DIR%\.." "%SRC_DIR%"
"%PYTHON%" -m pip install .
if errorlevel 1 exit 1