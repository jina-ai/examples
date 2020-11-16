# Build Bert-based NLP Semantic Search System (with incremental indexing)

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

In this demo, we use Jina to build a semantic search system, with the additional showcase of **incremental indexing**. 

**NOTE**: This example builds on the basic example presented in [here](../southpark-search/README.md). Please study and learn the concepts presented there and then come back to this one.


<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Running the example](#running-the-example)
- [Overview](#overview)
- [Documentation](#documentation)
- [Stay tuned](#stay-tuned)
- [License](#license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Running the example

**NOTE** Jina only works on Python 3.7 and 3.8

Install requirements.

`pip install -r requirements.txt`

Prepare data

`bash get_data.sh data`

This creates all the data in the `data` dir. Of main import will be `character-lines-1.csv` and `character-lines-2.csv`.

Run the indexing step

`python app.py -t index`

This will perform the indexing on the first file, stop the flow, re-start it, and then index the second. This showcases **incremental indexing**.

Query the data

`python app.py -t query`


## Overview

For the discussion on the basic topics, read through the documentation in the [South Park example](../southpark-search/README.md). This README will delve deeper into how we use **incremental indexing**.

### What is incremental indexing?

Briefly, this allows for the user to re-use an index to add new data. It also automatically handles adding documents with duplicate IDs. For a more in-depth explanation on how Jina handles this, refer to [this chapter](https://docs.jina.ai/chapters/prevent_duplicate_indexing/index.html) in our docs.

### Configuration changes

In order to adapt the South Park scripts example to support incremental indexing, we need to to the following:

1. Change the `indexer` in `flow-index` and `flow-query` to use `DocIDCache` as a filter (in the `uses_before` field). This ensures that we prevent duplicates.

    In this example the `DocIDCache` is separated into its own `.yml` file, in `index_cache`:
    
    ```yaml
    !DocIDCache
    with:
      index_path: cache.tmp
    metas:
      name: cache
      workspace: $JINA_WORKSPACE
    requests:
      on:
        [SearchRequest, TrainRequest, IndexRequest, ControlRequest]:
          - !RouteDriver {}
        IndexRequest:
          - !TaggingCacheDriver
            with:
              tags:
                is_indexed: true
          - !FilterQL
            with:
              lookups: {tags__is_indexed__neq: true}
    ```
    
    This might look complicated, but what it basically does is to first check the cache for any matching doc IDs, before indexing and querying.

2. Adapt dataset to highlight incremental indexing.

    We split the dataset into two files, `character-lines-1.csv` and `characters-lines-2.csv`. This way we can show how we can index one, close the `Flow` object, and then index the other.
    
    The env. var. `JINA_DATA_FILE` has also been split into two, with `JINA_DATA_FILE_1` and `JINA_DATA_FILE_2`. By default these are set to point to the two files above.

3. Adapt the `app.py` to index, close, and index again.

    When running `python app.py -t index` we would usually only index one file. We now have the following:
    
    ```python
    f = Flow().load_config("flow-index.yml")

    with f:
        print(f'Indexing file {os.environ["JINA_DATA_FILE_1"]}')
        f.index_lines(
        ...
        )

    # we then re-use the same index to append new data
    with f:
        print(f'Indexing file {os.environ["JINA_DATA_FILE_2"]}')
        f.index_lines(
           ...
        )    
    ```
    
    This indexes the first file, closes the flow, and then indexes a second file.


<!-- TODO --> 

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

## Stay tuned

- [Slack chanel](https://join.slack.com/t/jina-ai/shared_invite/zt-dkl7x8p0-rVCv~3Fdc3~Dpwx7T7XG8w) - a communication platform for developers to discuss Jina
- [Community newsletter](mailto:newsletter+subscribe@jina.ai) - subscribe to the latest update, release and event news of Jina
- [LinkedIn](https://www.linkedin.com/company/jinaai/) - get to know Jina AI as a company
- ![Twitter Follow](https://img.shields.io/twitter/follow/JinaAI_?label=Follow%20%40JinaAI_&style=social) - follow us and interact with us using hashtag `#JinaSearch`
- [Join Us](mailto:hr@jina.ai) - want to work full-time with us at Jina? We are hiring!
- [Company](https://jina.ai) - know more about our company, we are fully committed to open-source!


## License

Copyright (c) 2020 Jina AI Limited. All rights reserved.

Jina is licensed under the Apache License, Version 2.0. See [LICENSE](https://github.com/jina-ai/jina/blob/master/LICENSE) for the full license text.
