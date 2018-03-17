pyinstaller --log-level=DEBUG ^
--name "Little Geocoder" ^
--windowed ^
--noconfirm ^
--add-binary env/Lib/site-packages/PyQt5/Qt/plugins/platforms/qwindows.dll;platforms ^
--add-binary env/Lib/site-packages/PyQt5/Qt/plugins/styles/qwindowsvistastyle.dll;PyQt5/Qt/plugins/styles ^
--add-data app/worldwide.png;. ^
--onefile ^
--exclude-module scipy ^
--exclude-module matplotlib ^
--icon icon/worldwide.ico ^
--hidden-import="pandas._libs.tslibs.timedeltas" ^
app/app.py

python -c "import shutil;shutil.make_archive('release/LittleGeocoder.Win', 'zip', 'dist', 'Little Geocoder.exe')"
