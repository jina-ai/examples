#!/bin/sh
mkdir .workspace
kaggle datasets download -d neisse/scrapped-lyrics-from-6-genres
unzip scrapped-lyrics-from-6-genres.zip -d .workspace
rm -rf scrapped-lyrics-from-6-genres.zip
rm -rf .workspace/artists-data.csv
