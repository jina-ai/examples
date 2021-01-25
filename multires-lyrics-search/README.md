
# Lyrics Live Search: Understanding the Concept of Chunk

[![Jina](https://github.com/jina-ai/jina/blob/master/.github/badges/jina-badge.svg?raw=true  "We fully commit to open-source")](https://get.jina.ai)

[![](demo.gif)](https://www.youtube.com/watch?v=GzufeV8AY_w)

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Use toy data](#use-toy-data)
- [[Optional] Download full lyrics dataset](#optional-download-full-lyrics-dataset)
- [Install](#install)
- [Run](#run)
- [View in Browser](#view-in-browser)
- [License](#license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


## Use toy data

We have included 1000 lyrics as toy data in [`toy-data`](toy-data).
This data is ready to use with this example.

## [Optional] Download full lyrics dataset

**NOTE**: This is what is used in the Docker image and is **required** if you want to build it (the Docker image) yourself. 

If you want to use the full dataset, you can download it from kaggle (https://www.kaggle.com/neisse/scrapped-lyrics-from-6-genres).
To get it, once you have your Kaggle Token in your system as described in (https://www.kaggle.com/docs/api), run:

```bash
bash get_data.sh
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

## View in Browser

```bash
cd static
python -m http.server
```

Open `http://0.0.0.0:8000/` in your browser.

## Use Docker image from the jina hub

To make it easier for the user, we have built and published the [Docker image](https://hub.docker.com/r/jinahub/app.example.multireslyricssearch) with 10000 indexed songs (more than the toy example, but just a small part of the huge dataset).
You can retrieve the docker image using:

```bash
docker pull jinahub/app.example.multireslyricssearch:0.0.2-0.9.20
```
So you can pull from its latest tags.

Then you can run it, and you can proceed to see the results in the browser as explained before

```bash
docker run -p 65481:65481 jinahub/app.example.multireslyricssearch:0.0.2-0.9.20
```


## License

Copyright (c) 2020-2021 Han Xiao. All rights reserved.
