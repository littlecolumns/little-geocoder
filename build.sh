#!/bin/bash

pyinstaller \
	--log-level=DEBUG \
	--name "Simple Visual Geocoder" \
	--windowed \
	--noconfirm \
  --hidden-import="pandas._libs.tslibs.timedeltas" \
	--onefile \
  --osx-bundle-identifier "com.jonathansoma.visual-geocoder" \
	-i icon/browser.icns \
	app/app.py

codesign -s "$CODESIGN_ID" "dist/Simple Visual Geocoder.app"

cd dist && zip -r "../release/SimpleVisualGeocoder.zip" "Simple Visual Geocoder.app"
