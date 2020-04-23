# Video Semantic Search in Scale with Prefetching and Sharding 

This demo shows how to use Jina to build a video search engine.

## Prerequirements

This demo requires Python 3.7.

```bash
pip install -r requirements.txt
```

You also need to have Jina installed, please refer to [the installation guide](https://github.com/jina-ai/jina#getting-started), in particular following [the recommended way for developers](https://github.com/jina-ai/jina#dev-mode-install-from-your-local-folkclone).

## Download the data

```bash
python gif_download.py
```

There are quite some data, you may want to modify this code or [the file list](data/tgif-v1.0.tsv) to get only part of them.


## Run Index

```bash
python app.py
```

## Run Query

```bash
# change the Line 12 of app.py to 
# RUN_MODE = 'debug-query'
python app.py
```
