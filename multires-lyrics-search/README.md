# Lyrics Live Search: Understanding the Concept of Chunk

[![Jina](https://github.com/jina-ai/jina/blob/master/.github/badges/jina-badge.svg?raw=true  "We fully commit to open-source")](https://get.jina.ai)

[![](demo.gif)](https://www.youtube.com/watch?v=GzufeV8AY_w)


## Download lyrics data

We have included 1000 lyrics as toy data in [`toy-data`](toy-data). Please download the full data via:

```bash
pip install kaggle
kaggle datasets download -d neisse/scrapped-lyrics-from-6-genres
```

Move `lyrics-data.csv` to `data/`

## Install

```bash
pip install .
```

To install it in editable mode

```bash
pip install -e .
```

## Run

| Command | Description |
| :--- | :--- |
|``python app.py index`` | To index files/data |
| ``python app.py query`` | To run query on the index | 
| ``python app.py dryrun`` | Sanity check on the topology | 

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
```

## View in Browser

```bash
cd static
python -m SimpleHTTPServer
```

Open `index.html` in your browser.


## License

Copyright (c) 2020 Han Xiao. All rights reserved.


