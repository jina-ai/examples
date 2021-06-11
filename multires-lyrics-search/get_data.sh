#!/bin/sh
kaggle datasets download -d neisse/scrapped-lyrics-from-6-genres
unzip scrapped-lyrics-from-6-genres.zip
rm -rf scrapped-lyrics-from-6-genres.zip
rm -rf artists-data.csv
mv lyrics-data.csv lyrics-data/lyrics-data.csv
