# Build a Search system using Facebook AI Similarity Search (FAISS) as vector database <!-- omit in toc -->

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

In this demo, we use Jina to build a vector search engine that finds the closest vector in the database to a query. We will use the Facebook AI Similarity Search, ([FAISS](https://github.com/facebookresearch/faiss)), which is a library for efficient similarity search and clustering of dense vectors. This example uses [ANN_SIFT10K](http://corpus-texmex.irisa.fr/), which is a dataset comprised of three vectors:  

- 10K index
- 100 vectors query
- 25K vectors to train
  
These vectors are [SIFT](https://en.wikipedia.org/wiki/Scale-invariant_feature_transform) descriptors for some image dataset. The example is easily adapted for use with larger datasets from the same source which can be found [here](http://corpus-texmex.irisa.fr/). For this demo, a vector is considered to be a document and only one chunk per document is used.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents**

- [Prerequirements](#prerequirements)
- [Prepare the data](#prepare-the-data)
- [Define the Flows](#define-the-flows)
  - [Index](#index)
  - [Query](#query)
- [Run the Flows](#run-the-flows)
  - [Index](#index-1)
  - [Query](#query-1)
- [Dive into the FaissIndexer](#dive-into-the-faissindexer)
- [Evaluate the results](#evaluate-the-results)
- [Wrap up](#wrap-up)
- [Next Steps](#next-steps)
- [Documentation](#documentation)
- [Community](#community)
- [License](#license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Prerequirements

- Python 3.7
- [Jina installation](https://github.com/jina-ai/jina#get-started)

Additionally, since FAISS introduces many dependencies, the [Jina hub image](https://github.com/jina-ai/jina-hub/tree/master/indexers/vector/FaissIndexer) is used for simplicity.

## Prepare the data

FAISS needs to learn some structural patterns of the data in order to build an efficient indexing scheme. Usually, the training is done with some subset of data that is not necessarily part of the index.

Running these scripts will set you up to use the example. It will fetch the ANN_SIFT10K dataset files and generate a workspace folder where the training data will be stored.

This workspace folder will contain the built index once the vectors are indexed and will be mapped to the docker image.

```bash
./get_siftsmall.sh
./generate_training_data.sh
```

## Define the Flows

### Index

To index the data we first need to define our **Flow**. Here we use **YAML** file to define the Flow. In the Flow YAML file, we add **Pods** in sequence. In this demo, we have 5 pods defined with the name of `crafter`, `encoder`, `faiss_indexer`, `doc_indexer`, and `join_all`. 

However, we have another Pod working in silent. Actually, the input to the very first Pod is always the Pod with the name of **gateway**, the Forgotten Pod. For most time, we can safely ignore the **gateway** because it basically do the dirty orchestration work for the Flow.

<table style="margin-left:auto;margin-right:auto;">
<tr>
<td> flow-index.yml</td>
</tr>
<tr>
<td>
  <sub>

```yaml
!Flow
metas:
  prefetch: 10
pods:
  crafter:
    uses: _forward
  encoder:
    uses: yaml/encode.yml
    parallel: $PARALLEL
  indexer:
    uses: jinaai/hub.executors.indexers.vector.faiss:latest
    parallel: $PARALLEL
    timeout_ready: 600000
    uses_internal: yaml/indexer.yml
    volumes: './workspace'
```
</sub>
</td>
</tr>
</table>

### Query

As in the indexing time, we also need a Flow to process the request message during querying. The only difference with its index counterpart is that `doc_indexer` is piped to the `faiss_indexer` with a `ranker` in the middle.
<table  style="margin-left:auto;margin-right:auto;">
<tr>
<td> flow-query.yml</td>
</tr>
<tr>
<td>
  <sub>

```yaml
!Flow
with:
  read_only: true
pods:
  crafter:
    uses: _forward
  encoder:
    uses: yaml/encode.yml
    parallel: $PARALLEL
  indexer:
    uses: jinaai/hub.executors.indexers.vector.faiss:latest
    parallel: $PARALLEL
    timeout_ready: 600000
    uses_internal: yaml/query-indexer.yml
    volumes: './workspace'
  ranker:
    uses: MinRanker
```

</sub>

</td>
</tr>
</table>

In this Flow, the `faiss_indexer` is the one that will do the nearest neighbours search from the given chunk (in this case, since every document has one chunk they are the same). Later, the `MinRanker` ranks the chunks by min score value from all the retrieved chunks from `faiss_indexer`, Later, `doc_indexer` retrieves the actual document value from the Document Id.

## Run the Flows

### Index 

Index is run with the following command, where batch_size can be chosen by the user. Indexing reads a file of numpy arrays, and sends them to the flow gateway in binary mode to be converted back into numpy arrays by the crafter.

```bash
python app.py -t index -n 10000
```

### Query

Query can be run with the following command.

```bash
python app.py -t query
```

## Dive into the FaissIndexer

The main contribution of this example is to try and understand how FAISS can be used to build the index. To understand how it works, let's take a look at the yaml file used to construct the `faiss_indexer`. It is important to note that `faiss_indexer` will run inside a docker image.

Let's take a look at `yaml/indexer.yml`

```yaml
!CompoundIndexer
components:
  - !NumpyIndexer
    with:
      index_filename: 'faiss_index.tgz'
    metas:
      workspace: './workspace'
      name: wrapidx
  - !BinaryPbIndexer
    with:
      index_filename: doc.gz
    metas:
      name: docidx
      workspace: './workspace'
metas:
  name: indexer
  workspace: './workspace'
requests:
  on:
    IndexRequest:
      - !VectorIndexDriver
        with:
          executor: wrapidx
      - !KVIndexDriver
        with:
          executor: docidx
    ControlRequest:
      - !ControlReqDriver {}
```

The chunk indexer is formed by a CompoundExecutor composed by a `FaissIndexer` and a `ChunkPbIndexer`. Having a vector indexer such as `FaissIndexer` composed with a key-value indexer is a common pattern in Jina since the vector indexer will do the similarity search and the key-value one will keep track of the actual chunk values.

As we can see, `FaissIndexer` receives 3 parameters:

- [`index_key`]: Relates to parameters used in the faiss [index factory](https://github.com/facebookresearch/faiss/wiki/The-index-factory) which determine types of inverted indexes and encoders used to index the vectors.
- [`index_filename`]: File name where to store the index.
- [`train_filepath`]: Path where to find the data needed to train the index.

## Evaluate the results

This demo also outputs the evaluation of search system. The used metric is recall@k where only the true nearest neighbor is considered to be a relevant document.
Therefore, it computes how many times the true nearest neighbour is returned as one of the k closest vectors from a query. 

With the default demo, the results are:

- recall@1: 0.26
- recall@10: 0.56
- recall@50: 0.7
- recall@100: 0.74

Using more complex inverted indices and encoders (different `index_key`) should lead to better results.
Using `index_key: 'Flat'` gives a recall equal to 1 because it is the exhaustive search mode for FAISS. To learn more about the range of supported keys and options, be sure to visit [FAISS indexes](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes).

## Wrap up

In this example we have seen how to use `FaissIndexer` to use FAISS as a vector database. We also have seen how to use a pod inside a docker container inside our index and query flows.

**Enjoy Coding with Jina!**

## Next Steps

Going forward, try:  

- different kinds of inverted indices and options from FAISS.
- other indexers or rankers.
- indexing larger datasets.

Finally, play around with different evaluation metrics.

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

Copyright (c) 2020 Jina AI Limited. All rights reserved.

Jina is licensed under the Apache License, Version 2.0. See [LICENSE](https://github.com/jina-ai/jina/blob/master/LICENSE) for the full license text.
