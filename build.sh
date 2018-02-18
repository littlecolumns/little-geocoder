#!/bin/bash

pyinstaller \
	--log-level=DEBUG \
	--name "Simple Visual Geocoder" \
	--windowed \
  --add-binary env/lib/python3.6/site-packages/PyQt5/Qt/plugins/styles/libqmacstyle.dylib:plugins/styles \
  --add-data app/worldwide.png:. \
	--noconfirm \
  --hidden-import="pandas._libs.tslibs.timedeltas" \
	--onefile \
  --exclude-module scipy \
  --exclude-module matplotlib \
  --osx-bundle-identifier "com.jonathansoma.visual-geocoder" \
	-i icon/worldwide.icns \
	app/app.py

codesign -s "$CODESIGN_ID" "dist/Simple Visual Geocoder.app"

cd dist && zip -r "../release/SimpleVisualGeocoder.OSX.zip" "Simple Visual Geocoder.app"
