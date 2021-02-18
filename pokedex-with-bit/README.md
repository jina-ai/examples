# Search Pokemon Images with Jina

In this example, we use [BiT (Big Transfer)](https://github.com/google-research/big_transfer), to build an end-to-end **neural image search** system. You can use this demo to index an image dataset and query the most similar image from it. 

Features that come out of the box:

- Interactive query
- Index with shards
- REST and gRPC gateway
- Dashboard monitor

To save you from dependency hell, we'll use the containerized version in these instructions. That means you only need to have [Docker installed](https://docs.docker.com/get-docker/). No Python virtualenv, no Python package (un)install.

**NOTE** Use Python 3.7 for this example. 

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [TL;DR: Just Show Me the Pokemon!](#tldr-just-show-me-the-pokemon)
- [Download and Extract Data](#download-and-extract-data)
- [Run outside of Docker](#run-outside-of-docker)
- [Run in Docker](#run-in-docker)
- [Troubleshooting](#troubleshooting)
- [Documentation](#documentation)
- [Community](#community)
- [License](#license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


## Query from Docker

> *I want Pokémon! I don't care about Jina cloud-native neural search or whatever big names you throw around, just show me the Pokémon!*

We have a pre-built Docker image ready to use, you need to run this on your console:

```bash
docker run -p 45678:45678 jinahub/app.example.pokedexwithbit:0.0.1-0.9.20
```

So now you're ready to query! And for that you have two options:

 - You can use [Jinabox.js](https://jina.ai/jinabox.js/) to find the Pokemon which matches most clearly. Just set the endpoint to `http://127.0.0.1:45678/api/search` and drag from the thumbnails on the left or from your file manager.
 - Or you can `curl`/query/js it via HTTP POST request. [Details here](#query-via-rest-api). 

## Run without Docker

### Download and Extract Data

For this example we're using Pokemon sprites from [veekun.com](https://veekun.com/dex/downloads). To download them run:

```sh
sh ./get_data.sh
```

### Download and Extract Pretrained Model

In this example we use [BiT (Big Transfer) model](https://github.com/google-research/big_transfer), To download it:

```sh
sh ./download.sh
```

### Index Data

```sh
python app.py index
```

After this you should see a new `workspace` folder, which contains all the encoded data generated during indexing. 

### Query Data

```python
python app.py search
```

And then follow the Jinabox instructions from the [Query from Docker](#query-from-docker) section above.

#### Diving Deeper

Jina's REST API uses the [data URI scheme](https://en.wikipedia.org/wiki/Data_URI_scheme) to represent multimedia data. To query your indexed data, simply organize your picture(s) into this scheme and send a POST request to `http://0.0.0.0:45678/api/search`, e.g.:

```bash
curl --verbose --request POST -d '{"top_k": 10, "mode": "search",  "data": ["data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAIAAABLbSncAAAA2ElEQVR4nADIADf/AxWcWRUeCEeBO68T3u1qLWarHqMaxDnxhAEaLh0Ssu6ZGfnKcjP4CeDLoJok3o4aOPYAJocsjktZfo4Z7Q/WR1UTgppAAdguAhR+AUm9AnqRH2jgdBZ0R+kKxAFoAME32BL7fwQbcLzhw+dXMmY9BS9K8EarXyWLH8VYK1MACkxlLTY4Eh69XfjpROqjE7P0AeBx6DGmA8/lRRlTCmPkL196pC0aWBkVs2wyjqb/LABVYL8Xgeomjl3VtEMxAeaUrGvnIawVh/oBAAD///GwU6v3yCoVAAAAAElFTkSuQmCC", "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAIAAABLbSncAAAA2ElEQVR4nADIADf/AvdGjTZeOlQq07xSYPgJjlWRwfWEBx2+CgAVrPrP+O5ghhOa+a0cocoWnaMJFAsBuCQCgiJOKDBcIQTiLieOrPD/cp/6iZ/Iu4HqAh5dGzggIQVJI3WqTxwVTDjs5XJOy38AlgHoaKgY+xJEXeFTyR7FOfF7JNWjs3b8evQE6B2dTDvQZx3n3Rz6rgOtVlaZRLvR9geCAxuY3G+0mepEAhrTISES3bwPWYYi48OUrQOc//IaJeij9xZGGmDIG9kc73fNI7eA8VMBAAD//0SxXMMT90UdAAAAAElFTkSuQmCC"]}' -H 'Content-Type: application/json' 'http://0.0.0.0:34567/api/search'
```

[JSON payload syntax and spec can be found in the docs](https://docs.jina.ai/chapters/restapi/#).

The above explains how to use a REST gateway, but by default Jina uses a gRPC gateway, which has much higher performance and richer features. Read our [documentation on Jina IO](https://docs.jina.ai/chapters/io/#) for more information.

### Build a Docker Image

After playing with it for a while, you may want to change the code and rebuild the image. Simply run:
```bash
docker build -t jinaai/app.examples.pokedexwithbit .
```

## Monitor Progress

If it's running successfully, you should be able to see logs scrolling in the console and in the dashboard:

<p align="center">
  <img src=".github/.README_images/0a8863abb3fcee182e1fe8fe46c47b7a.gif?raw=true" alt="Jina banner" width="45%">
  <img src=".github/.README_images/ed2907cd11ac26a2a3a2555f16071d13.gif?raw=true" alt="Jina banner" width="45%">
</p>

Under `$(pwd)/workspace`, you'll see a list of directories `chunk_compound_indexer-*` after indexing. This is because we set shards to 8.

## Troubleshooting

### Memory Issues

BiT model seems pretty resource-hungry. If you are using Docker Desktop, make sure to assign enough memory for your Docker container, especially when you have multiple shards. Below are my MacOS settings with two shards:

<p align="center">
  <img src=".github/.README_images/d4165abd.png?raw=true" alt="Jina banner" width="80%">
</p>

### Incremental Indexing

Incremental indexing and entry-level deleting are yet not supported in this demo. Duplicate indexing may not throw exceptions, but may produce strange results. So make sure to clean `$(pwd)/workspace` before each run.

Meet other problems? Check our [troubleshooting guide](https://docs.jina.ai/chapters/troubleshooting.html) or [submit a Github issue](https://github.com/jina-ai/jina/issues/new/choose).


## License

Copyright (c) 2021 Jina AI Limited. All rights reserved.

Jina is licensed under the Apache License, Version 2.0. See [LICENSE](https://github.com/jina-ai/jina/blob/master/LICENSE) for the full license text.
