
# PDF search with Jina

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

This example demonstrates how [Jina](http://www.jina.ai) can be used to search a repository of PDF files. The example employs a multimodal search architecture, allowing a user to query the data by providing text, or an image, or both simultaneously.

What's included in this example:

- Search text, image, PDF all in one flow or in separate flows
- Leverage Jina Recursive Document Representation to segment and encode text
- Speed up indexing time with parallel Peas
- Use customized executors to better fit your needs
- Provide detailed docstrings for YAML files to help you understand Jina App

- [PDF search](#pdf-search)
  * [Use toy data](#use-toy-data)
  * [Install](#install)
  * [Run](#run)
  * [Start the Server](#start-the-server)
  * [Query via REST API](#query-via-rest-api)
  * [Documentation](#documentation)
  * [Community](#community)
  * [License](#license)
    

## Use toy data

We have included several PDF blogs as toy data in [`toy_data`](toy_data). This data is ready to use with this example.
You can also use other PDF files supported by [`pdfplumber`](https://github.com/jsvine/pdfplumber).

## Install

```bash
pip install -r requirements.txt
```

## Run

| Command | Description |
| :--- | :--- |
| ``python app.py -t index`` | To index files/data |
| ``python app.py -t query`` | To run a query flow for searching text, image, and PDF |
| ``python app.py -t query_text`` | To run a query flow for searching text |
| ``python app.py -t query_image`` | To run a query flow for searching image |
| ``python app.py -t query_pdf`` | To run a query flow for searching PDF |
| ``python app.py -t query_restful`` | To expose the restful API of the query flow for searching text, image, and PDF|
| ``python app.py -t dryrun`` | Sanity check on the topology |

## Start the Server

``` bash
python app.py -t query_restful
```

## Query via REST API

When the REST gateway is enabled, Jina uses the [data URI scheme](https://en.wikipedia.org/wiki/Data_URI_scheme) to represent multimedia data. Simply organize your picture(s) into this scheme and send a POST request to `http://0.0.0.0:45670/api/search`, e.g.:

``` bash
curl --request POST -d '{"top_k": 10, "mode": "search",  "data": ["jina hello multimodal"]}' -H 'Content-Type: application/json' 'http://0.0.0.0:45670/api/search'
```

[JSON payload syntax and spec can be found in the docs](https://docs.jina.ai/chapters/restapi/#).

This example shows you how to feed data into Jina via REST gateway. By default, Jina uses a gRPC gateway, which has much higher performance and rich features. If you are interested in that, go ahead and check out our [other examples](https://learn.jina.ai) and [read our documentation on Jina IO](https://docs.jina.ai/chapters/io/#).

## Understand the Flows

The following image shows the structure of index flow, the text and image will be extracted from PDF files as chunks. Then we will use 3 paths to process and store the data.
- For the first path, the DocIndexer will store the Document ID and Document data on disk
- For the second path, the pods will filter the image chunks, and do the processing. It will also store chunk ID and chunk data on disk
- For the third path, the pods will filter the text chunks, and further segment text into smaller chunks. The ChunkMeta indexer is used to store data at chunks level and text indexer is used to store data for chunks of chunks.
The joiner will wait until 3 paths are finished.

<p align="center">
  <img src=".github/.README_images/indexflow.png?raw=true" alt="Jina banner" width="90%">
</p>

The following image shows the structure of query flow. For query, we can send text, image and PDF files to one flow and get the results. We use 2 parallel paths to process the query data and get results.
- For the first path, we will get embedding of the image data and use image indexer to get the most similar matches at chunks level.
- For the second path, we will get embedding of the text data at chunks of chunks level in the text encoder. Then we use CCtoC ranker to get the matches from chunks of chunks (CC) level to chunks (C) level. The chunkmeta indexer can help to append meta data for matches of chunks.
The ChunktoRoot Ranker is used to get the matches at root level and then we can use the matches ID to get the documents data.

<p align="center">
  <img src=".github/.README_images/queryflow.png?raw=true" alt="Jina banner" width="90%">
</p>


## Documentation 

<a href="https://docs.jina.ai/">
<img align="right" width="350px" src="https://github.com/jina-ai/jina/blob/master/.github/jina-docs.png" />
</a>

The best way to learn Jina in depth is to read our documentation. Documentation is built on every push, merge, and release event of the master branch. You can find more details about the following topics in our documentation.

- [Jina command line interface arguments explained](https://docs.jina.ai/chapters/cli/index.html)
- [Jina Python API interface](https://docs.jina.ai/api/jina.html)
- [Jina YAML syntax for executor, driver and flow](https://docs.jina.ai/chapters/yaml/yaml.html)
- [Jina Protobuf schema](https://docs.jina.ai/chapters/proto/index.html)
- [Environment variables used in Jina](https://docs.jina.ai/chapters/envs.html)
- ... [and more](https://docs.jina.ai/index.html)

## Community

- [Slack channel](https://join.slack.com/t/jina-ai/shared_invite/zt-dkl7x8p0-rVCv~3Fdc3~Dpwx7T7XG8w) - a communication platform for developers to discuss Jina
- [Community newsletter](mailto:newsletter+subscribe@jina.ai) - subscribe to the latest update, release and event news of Jina
- [LinkedIn](https://www.linkedin.com/company/jinaai/) - get to know Jina AI as a company and find job opportunities
- [![Twitter Follow](https://img.shields.io/twitter/follow/JinaAI_?label=Follow%20%40JinaAI_&style=social)](https://twitter.com/JinaAI_) - follow us and interact with us using hashtag `#JinaSearch`  
- [Company](https://jina.ai) - know more about our company, we are fully committed to open-source!

## License

Copyright (c) 2021 Jina AI Limited. All rights reserved.

Jina is licensed under the Apache License, Version 2.0. See [LICENSE](https://github.com/jina-ai/jina/blob/master/LICENSE) for the full license text.
