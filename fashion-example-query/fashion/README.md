# Star Trek QueryLang

[![Jina](https://github.com/jina-ai/jina/blob/master/.github/badges/jina-badge.svg?raw=true  "We fully commit to open-source")](https://get.jina.ai)

A demo neural search project that uses Jina. Jina is the cloud-native neural search framework powered by state-of-the-art AI and deep learning.

## Features

## Install

```bash
pip install .
```

To install it in editable mode

```bash
pip install -e .
```
## Set environment variables

Set env variables like ```DATA_PATH``` and ```MAX_DOCS```
For example, relative from the data/ folder:
EXPORT DATA_PATH='./data/startrek_tng.csv'

## Run

| Command                  | Description                  |
| :---                     | :---                         |
| ``python app.py index``  | To index files/data          |
| ``python app.py search`` | To run query on the index    |
| ``python app.py dryrun`` | Sanity check on the topology |

## Run as a Docker Container

To build the docker image
```bash
docker build -t jinaai/hub.app.star_trek_querylang:0.0.1 .
```

To mount local directory and run:
```bash
docker run -v "$(pwd)/j:/workspace" jinaai/hub.app.star_trek_querylang:0.0.1
``` 

To query
```bash
docker run -p 65481:65481 -e "JINA_PORT=65481" jinaai/hub.app.star_trek_querylang:0.0.1 search
```
## Note:
The ```depth_range``` parameter in Flow and Pod YAML can be set according to the requirement of the implementation. This is used for recursive document structure in Jina.

## License

Copyright (c) 2020 Jina's friend. All rights reserved.


