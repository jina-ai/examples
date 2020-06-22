
# Google's Big Transfer Model in (Poké-)Production using Jina

<p align="center">
 
[![Jina](https://github.com/jina-ai/jina/blob/master/.github/badges/jina-badge.svg "We fully commit to open-source")](https://jina.ai)
[![Jina](https://github.com/jina-ai/jina/blob/master/.github/badges/jina-hello-world-badge.svg "Run Jina 'Hello, World!' without installing anything")](https://github.com/jina-ai/jina#jina-hello-world-)
[![Jina](https://github.com/jina-ai/jina/blob/master/.github/badges/license-badge.svg "Jina is licensed under Apache-2.0")](#license)
[![Jina Docs](https://github.com/jina-ai/jina/blob/master/.github/badges/docs-badge.svg "Checkout our docs and learn Jina")](https://docs.jina.ai)
[![We are hiring](https://github.com/jina-ai/jina/blob/master/.github/badges/jina-corp-badge-hiring.svg "We are hiring full-time position at Jina")](https://jobs.jina.ai)
<a href="https://twitter.com/intent/tweet?text=%F0%9F%91%8DCheck+out+Jina%3A+the+New+Open-Source+Solution+for+Neural+Information+Retrieval+%F0%9F%94%8D%40JinaAI_&url=https%3A%2F%2Fgithub.com%2Fjina-ai%2Fjina&hashtags=JinaSearch&original_referer=http%3A%2F%2Fgithub.com%2F&tw_p=tweetbutton" target="_blank">
  <img src="https://github.com/jina-ai/jina/blob/master/.github/badges/twitter-badge.svg"
       alt="tweet button" title="👍Share Jina with your friends on Twitter"></img>
</a>
[![Python 3.7 3.8](https://github.com/jina-ai/jina/blob/master/.github/badges/python-badge.svg "Jina supports Python 3.7 and above")](#)
[![Docker](https://github.com/jina-ai/jina/blob/master/.github/badges/docker-badge.svg "Jina is multi-arch ready, can run on differnt architectures")](https://hub.docker.com/r/jinaai/jina/tags)

</p>

In this example, we use [BiT (Big Transfer): the latest pretrained computer-vision model by Google](https://github.com/google-research/big_transfer), to build an end-to-end **neural image search** system. [Thanks to Jina](https://github.com/jina-ai/jina), you can see how easy it is to put an academic result released few days ago into the production (spoiler alert, this project takes me *2 hours* only). You can use this demo system to indexes image dataset and query the most similar image from it. In the example output below, first column in every row is the query, the rest is the top-k results. 

[![](.github/.README_images/7262e2aa.png)](https://get.jina.ai)

Features that come out of the box:

- interactive query
- parallel replicas
- index with shards
- containerization
- REST and gRPC gateway
- dashboard monitor

To save you from the dependency hell, I will use the containerized version in the following instructions. That means you only need to have [Docker installed](https://docs.docker.com/get-docker/). No Python virtual env, no python package (un)install. 

The code can of course run natively on your local machine, please [read Jina installation guide for details](https://docs.jina.ai/chapters/install/via-pip.html).

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Cotents**

- [TLDR;](#tldr)
- [Index Image Data](#index-image-data)
- [Query Top-K Visually Similar Images](#query-top-k-visually-similar-images)
- [Build Docker Image](#build-docker-image)
- [Troubleshooting](#troubleshooting)
- [Documentation](#documentation)
- [Stay tuned](#stay-tuned)
- [License](#license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


## TLDR;

> *I want Pokémon! I don't care what Jina cloud-native neural search or whatever big names you put there, just show me the Pokémon!*

We have a pre-built Docker image ready to use:

```bash
docker run -p 34567:34567 -e "JINA_PORT=34567" jinaai/hub.app.bitsearch-pokedex search
```

Then you can `curl`/query/js it via HTTP POST request. [Details can be found here](#query-via-rest-api).


## Index Image Data

We use BiT `R50x1` model in this example, you can change it in [`download.sh`]()

```bash
docker run -v "$(pwd)/data:/data" -v "$(pwd)/workspace:/workspace" -e "JINA_LOG_PROFILING=1" -p 5000:5000 jinaai/hub.app.bitsearch index
```

#### Command args explained
- `$(pwd)/data` is where all your images located (jpg/png are supported, but not support mix yet). You can change it to whatever path, just make sure it is absolute path
- `$(pwd)/workspace` is where Jina stores all indexes and other artifacts. 
- `"JINA_LOG_PROFILING=1" -p 5000:5000` are just for dashboard monitoring. They are optional. 

### Behind the scene

<table>
<tr>
<td> Python API </td>
<td> index.yml</td>
<td> <a href="https://github.com/jina-ai/dashboard">Flow in Dashboard</a></td>
</tr>
<tr>
<td> 

```python
from jina.flow import Flow

f = Flow.load_config('flow-index.yml')

with f:
    f.index(input_fn, batch_size=128)
```

</td>
<td>
  <sub>

```yaml
!Flow
with:
  logserver: true
pods:
  crafter:
    yaml_path: pods/craft.yml
    read_only: true
  encoder:
    yaml_path: pods/encode.yml
    replicas: $REPLICAS
    timeout_ready: 600000
    read_only: true
  chunk_idx:
    yaml_path: pods/chunk.yml
    replicas: $SHARDS
    separated_workspace: true
  doc_idx:
    yaml_path: pods/doc.yml
    needs: crafter
  join_all:
    yaml_path: _merge
    needs: [doc_idx, chunk_idx]
```

</sub>

</td>
<td>

![Flow in Dashboard](.github/.README_images/6d28795b.png?raw=true)

</td>
</tr>
</table>

### Index Result

With a successful running, you should be able to see logs rolling in the console and in the dashboard:

<p align="center">
  <img src=".github/.README_images/0a8863abb3fcee182e1fe8fe46c47b7a.gif?raw=true" alt="Jina banner" width="45%">
  <img src=".github/.README_images/ed2907cd11ac26a2a3a2555f16071d13.gif?raw=true" alt="Jina banner" width="45%">
</p>

Under `$(pwd)/workspace`, You will see a list of directories `chunk_compound_indexer-*` after indexing. This is because I set shards to 8.

## Query Top-K Visually Similar Images

### Start the Jina server
```bash
docker run -v "$(pwd)/workspace:/workspace" -p 34567:34567 -e "JINA_PORT=34567" jinaai/hub.app.bitsearch search
```

#### Command args explained
- `$(pwd)/workspace` is where Jina previosly stored all indexes and other artifacts. Now we need to load them.
- `-p 34567:34567 -e "PUB_PORT=34567"` is the REST API port 

### Query via REST API

When REST gateway is enabled, Jina use [data URI scheme](https://en.wikipedia.org/wiki/Data_URI_scheme) to represent multi-media data. Simply organize your picture(s) into this scheme and send a POST request to `http://0.0.0.0:34567/api/search`, e.g.:

```bash
curl --verbose --request POST -d '{"top_k": 10, "mode": "search",  "data": ["data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAIAAABLbSncAAAA2ElEQVR4nADIADf/AxWcWRUeCEeBO68T3u1qLWarHqMaxDnxhAEaLh0Ssu6ZGfnKcjP4CeDLoJok3o4aOPYAJocsjktZfo4Z7Q/WR1UTgppAAdguAhR+AUm9AnqRH2jgdBZ0R+kKxAFoAME32BL7fwQbcLzhw+dXMmY9BS9K8EarXyWLH8VYK1MACkxlLTY4Eh69XfjpROqjE7P0AeBx6DGmA8/lRRlTCmPkL196pC0aWBkVs2wyjqb/LABVYL8Xgeomjl3VtEMxAeaUrGvnIawVh/oBAAD///GwU6v3yCoVAAAAAElFTkSuQmCC", "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAIAAABLbSncAAAA2ElEQVR4nADIADf/AvdGjTZeOlQq07xSYPgJjlWRwfWEBx2+CgAVrPrP+O5ghhOa+a0cocoWnaMJFAsBuCQCgiJOKDBcIQTiLieOrPD/cp/6iZ/Iu4HqAh5dGzggIQVJI3WqTxwVTDjs5XJOy38AlgHoaKgY+xJEXeFTyR7FOfF7JNWjs3b8evQE6B2dTDvQZx3n3Rz6rgOtVlaZRLvR9geCAxuY3G+0mepEAhrTISES3bwPWYYi48OUrQOc//IaJeij9xZGGmDIG9kc73fNI7eA8VMBAAD//0SxXMMT90UdAAAAAElFTkSuQmCC"]}' -H 'Content-Type: application/json' 'http://0.0.0.0:34567/api/search'
```

[JSON payload syntax and spec can be found in the docs](https://docs.jina.ai/chapters/restapi/main.html).

This example shows how to feed data into Jina via REST gateway. By default, Jina use gRPC gateway, which has much higher performance and rich feature. If you are interested in that, go ahead and check out our [other examples](https://learn.jina.ai) and [read our documentation on Jina IO](https://docs.jina.ai/chapters/io/main.html).

### Query Results in Batch

Let's test the results on Pokémon! This time we use gRPC gateway (for better efficiency in batch query), simply run `python make_html.py`

<p align="center">
  <img src=".github/.README_images/f2dcf24c452f73b085c0108867f4ff33.gif?raw=true" alt="Jina banner" width="80%">
</p>

## Build Docker Image

After play it for a while, you may want to change the code and rebuild the image. Simply do
```bash
docker build -t jinaai/hub.app.bitsearch .
```

If you want to keep up with Jina's master branch, then pull before build:
```bash
docker pull jinaai/jina:devel
docker build -t jinaai/hub.app.bitsearch .
```

## Troubleshooting

### Memory issue

BiT model seems pretty resource-hungry. If you are using Docker Desktop, make sure you assign enough memory for your Docker container, especially when you have multiple replicas. Below is my MacOS settings with two replicas:


<p align="center">
  <img src=".github/.README_images/d4165abd.png?raw=true" alt="Jina banner" width="80%">
</p>

### Incremental indexing

Incremental indexing and entry-level deleting are not supported yet in this demo. Duplicate indexing may not throw exceptions, but may produce strange results. So make sure to clean `$(pwd)/workspace` before each run.

Meet other problems? Check our [troubleshooting guide](https://docs.jina.ai/chapters/troubleshooting.html). Or submit a Github issue.



## Documentation 

<a href="https://docs.jina.ai/">
<img align="right" width="350px" src="https://github.com/jina-ai/jina/blob/master/.github/jina-docs.png" />
</a>

The best way to learn Jina in depth is to read our documentation. Documentation is built on every push, merge, and release event of the master branch. You can find more details about the following topics in our documentation.

- [Jina command line interface arguments explained](https://docs.jina.ai/chapters/cli/main.html)
- [Jina Python API interface](https://docs.jina.ai/api/jina.html)
- [Jina YAML syntax for executor, driver and flow](https://docs.jina.ai/chapters/yaml/yaml.html)
- [Jina Protobuf schema](https://docs.jina.ai/chapters/proto/main.html)
- [Environment variables used in Jina](https://docs.jina.ai/chapters/envs.html)
- ... [and more](https://docs.jina.ai/index.html)

## Community

- [Slack channel](https://join.slack.com/t/jina-ai/shared_invite/zt-dkl7x8p0-rVCv~3Fdc3~Dpwx7T7XG8w) - a communication platform for developers to discuss Jina
- [Community newsletter](mailto:newsletter+subscribe@jina.ai) - subscribe to the latest update, release and event news of Jina
- [LinkedIn](https://www.linkedin.com/company/jinaai/) - get to know Jina AI as a company and find job opportunities
- [![Twitter Follow](https://img.shields.io/twitter/follow/JinaAI_?label=Follow%20%40JinaAI_&style=social)](https://twitter.com/JinaAI_) - follow us and interact with us using hashtag `#JinaSearch`  
- [Company](https://jina.ai) - know more about our company, we are fully committed to open-source!



## License

Copyright (c) 2020 Jina AI Limited. All rights reserved.

Jina is licensed under the Apache License, Version 2.0. See [LICENSE](https://github.com/jina-ai/jina/blob/master/LICENSE) for the full license text.
