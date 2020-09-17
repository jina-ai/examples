
# Lyrics Live Search: Understanding the Concept of Chunk

[![Jina](https://github.com/jina-ai/jina/blob/master/.github/badges/jina-badge.svg?raw=true  "We fully commit to open-source")](https://get.jina.ai)

[![](demo.gif)](https://www.youtube.com/watch?v=GzufeV8AY_w)

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Use toy data](#use-toy-data)
- [Download lyrics data](#download-lyrics-data)
- [Install](#install)
- [Run](#run)
- [View in Browser](#view-in-browser)
- [License](#license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


## Use toy data

We have included 1000 lyrics as toy data in [`toy-data`](toy-data).
This data is ready to use with this example.

## [Optional] Download full lyrics dataset

If you want to use the full dataset, please run:

```bash
pip install kaggle
mkdir data
kaggle datasets download -d neisse/scrapped-lyrics-from-6-genres
unzip scrapped-lyrics-from-6-genres.zip
mv lyrics-data data
export JINA_DATA_PATH=data/lyrics-data.csv
```

## Install

```bash
pip install -r requirements.txt
```

## Run

| Command | Description |
| :--- | :--- |
| ``python app.py index`` | To index files/data |
| ``python app.py search`` | To run query on the index |
| ``python app.py dryrun`` | Sanity check on the topology |

<!--
## Run as a Docker Container

To build the docker image
```bash
docker build -t jinaai/hub.app.multires_lyrics_search:0.0.1 .
```

To mount local directory and run:
```bash
docker run -v "$(pwd)/j:/workspace" jinaai/hub.app.multires_lyrics_search:0.0.1
```

To query
```bash
docker run -p 65481:65481 -e "JINA_PORT=65481" jinaai/hub.app.multires_lyrics_search:0.0.1 search
``` -->

## View in Browser

```bash
cd static
python -m http.server
```

Open `http://0.0.0.0:8000/` in your browser.


## License

Copyright (c) 2020 Han Xiao. All rights reserved.


