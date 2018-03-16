#!/bin/bash

pyinstaller \
	--log-level=DEBUG \
	--name "Little Geocoder" \
	--windowed \
  --add-binary env/lib/python3.6/site-packages/PyQt5/Qt/plugins/styles/libqmacstyle.dylib:plugins/styles \
  --add-data app/worldwide.png:. \
	--noconfirm \
  --hidden-import="pandas._libs.tslibs.timedeltas" \
	--onefile \
  --exclude-module scipy \
  --exclude-module matplotlib \
  --osx-bundle-identifier "com.littlecolumns.little-geocoder" \
	-i icon/worldwide.icns \
	app/app.py

codesign -s "$CODESIGN_ID" "dist/Little Geocoder.app"

cd dist && zip -r "../release/LittleGeocoder.OSX.zip" "Little Geocoder.app"
