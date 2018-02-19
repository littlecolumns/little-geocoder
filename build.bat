pyinstaller --log-level=DEBUG ^
--name "Simple Visual Geocoder" ^
--windowed ^
--noconfirm ^
--add-binary env/Lib/site-packages/PyQt5\Qt\plugins\platforms\qwindows.dll;platforms ^
--add-data app/worldwide.png;. ^
--onefile ^
--exclude-module scipy ^
--exclude-module matplotlib ^
--icon icon/worldwide.ico ^
--hidden-import="pandas._libs.tslibs.timedeltas" ^
app/app.py
python -c "import shutil;shutil.make_archive('release/SimpleVisualGeocoder.Win', 'zip', 'dist', 'Simple Visual Geocoder.exe')"
