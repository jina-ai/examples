# Build a Search system using Facebook AI Similarity Search (FAISS) or Annoy as vector database <!-- omit in toc -->

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

In this demo, we use Jina to build a vector search engine that finds the closest vector in the database to a query

This example is prepared to use one of these 2 datasets [ANN_SIFT10K or ANN_SIFT1M](http://corpus-texmex.irisa.fr/), which are datasets comprised of three vector sets:  

- 10K or 1M index
- 100 or 10K vectors query
- 25K or 100k vectors to train

To run the local example, we show here the steps to work with ANN_SIFT10K (siftsmall). A [docker image](https://hub.docker.com/r/jinahub/app.example.advancedvectorsearch) is published where the ANN_SIFT1M (sift) has already been indexed
using 4 shards.
  
These vectors are [SIFT](https://en.wikipedia.org/wiki/Scale-invariant_feature_transform) descriptors for some image dataset. The example is easily adapted for use with larger datasets from the same source which can be found [here](http://corpus-texmex.irisa.fr/). For this demo, a vector is considered to be a Document.

In this example, we use [Faiss](https://hub.docker.com/r/jinahub/pod.indexer.faissindexer) and [Annoy](https://hub.docker.com/r/jinahub/pod.indexer.annoyindexer) Indexer Vectors from the hub.

This example will show how the same index created with an index Flow can be used to be queried using different type of indexers.

This example also shows how to evaluate ranking results with the different indexers, and adds the search with NumpyIndexer (that uses exhaustive search) (close to 100% recall) to compare 

Before moving forward, we highly suggest completing/reviewing our lovely [Jina 101](https://github.com/jina-ai/jina/tree/master/docs/chapters/101) and [Jina "Hello, World!"👋🌍](https://github.com/jina-ai/jina#jina-hello-world-).

We encourage you to try different indexers and different options for other indexers to see what gets the best results and performance.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Requirements](#requirements)
- [Prepare the data](#prepare-the-data)
- [Define the Flows](#define-the-flows)
- [Run the Flows](#run-the-flows)
- [Dive into the `FaissIndexer`](#dive-into-the-faissindexer)
- [Evaluate the results](#evaluate-the-results)
- [Wrap up](#wrap-up)
- [Next Steps](#next-steps)
- [Documentation](#documentation)
- [Community](#community)
- [License](#license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Requirements

Be sure to create an environment with Python 3.7 or higher installed, then you also need to have the requirements of this example,
which are `jina`, `docker` and `click`.

In order to run the example with the different indexers, make sure to pull the docker images from the [Jina Hub repository](https://hub.docker.com/u/jinahub)

## Prepare the data

In order to get the data needed to run the example, we have prepared a small script that will download the required fails.
In this e

```bash
./get_data.sh siftsmall
```

Moreover, FAISS needs to learn some structural patterns of the data in order to build an efficient indexing scheme. Usually, the training is done with some subset of data that is not necessarily part of the index.

Running these scripts will set you up the rest of the way for this example by:

1. downloading the ANN_SIFT10K dataset files and
2. generating a workspace folder where the training data will be stored

This workspace folder will contain the built index once the vectors are indexed and will be mapped to the docker image.

```bash
./generate_training_data.sh
```

## Define the Flows

### Index <!-- omit in toc -->

To index the data we first need to define our **Flow** and for this example we'll use a **YAML** file. In the Flow YAML file, we add **Pods** in sequence. In this demo, we have five pods defined:

- `encoder`
- `indexer`

However, we have another Pod working in silence. Actually, the input to the very first Pod is always the Pod with the name of **gateway**, aka the "Forgotten" Pod. Most of the time, we can safely ignore the **gateway** because it essentially does the dirty work of orchestrating the work for the Flow.

<table style="margin-left:auto;margin-right:auto;">
<tr>
<td> flow-index.yml</td>
</tr>
<tr>
<td>
  <sub>

```yaml
!Flow
version: '1'
pods:
  - name: encoder
    uses: yaml/encode.yml
    shards: $JINA_PARALLEL
  - name: indexer
    uses: yaml/indexer.yml
    shards: $JINA_SHARDS
    timeout_ready: 10000
    polling: any
```
</sub>
</td>
</tr>
</table>

### Query <!-- omit in toc -->

Just as we need to index, we also need a Flow to process the request message during querying. The query flow looks very similar
to the index flow but with an extra pod used to evaluate results.

<table  style="margin-left:auto;margin-right:auto;">
<tr>
<td> flow-query.yml</td>
</tr>
<tr>
<td>
  <sub>

```yaml
!Flow
version: '1'
env:
  OMP_NUM_THREADS: ${{OMP_NUM_THREADS}}
with:
  read_only: true
pods:
  - name: encoder
    show_exc_info: true
    uses: yaml/encode.yml
    shards: $JINA_PARALLEL
  - name: indexer
    polling: all
    show_exc_info: true
    uses: $JINA_USES
    uses_internal: $JINA_USES_INTERNAL
    shards: $JINA_SHARDS
    timeout_ready: -1
    uses_after: yaml/merge-matches-sort.yml
    volumes: './workspace:/docker-workspace'
    remove_uses_ba: true
    docker_kwargs:
      environment:
        JINA_FAISS_INDEX_KEY: $JINA_FAISS_INDEX_KEY
        JINA_FAISS_DISTANCE: $JINA_FAISS_DISTANCE
        JINA_FAISS_NORMALIZE: $JINA_FAISS_NORMALIZE
        JINA_FAISS_NPROBE: $JINA_FAISS_NPROBE
        JINA_ANNOY_METRIC: $JINA_ANNOY_METRIC
        JINA_ANNOY_NTREES: $JINA_ANNOY_NTREES
        JINA_ANNOY_SEARCH_K: $JINA_ANNOY_SEARCH_K
        OMP_NUM_THREADS: ${{OMP_NUM_THREADS}}
  - name: evaluate
    show_exc_info: true
    uses: yaml/evaluate.yml
```

All the `environment` variables are added so that it is easy for the user to try out different configurations of `annoy` or `faiss` indexers.

</sub>

</td>
</tr>
</table>

In this Flow, the `faiss_indexer` is the one that will do the nearest neighbours search from the given chunk (in this case, since every document has one chunk they are the same). Additionally, it will return the top_k most similiar documents in order of similiarity. Later, `doc_indexer` retrieves the actual document value from the Document Id.

## Run the Flows

### Index <!-- omit in toc -->

Index is run with the following command, where batch_size can be chosen by the user. Indexing reads a file of numpy arrays, and sends them to the flow gateway in binary mode to be converted back into numpy arrays by the crafter.

```bash
python app.py -t index
```

### Query <!-- omit in toc -->

Query can be run with the following command, where index_type can be `annoy`, `faiss`, or `numpy`.
It is important to make sure that the environment variables in `app.py` are set to the right docker image tags that one wants to test.

```bash
python app.py -t query -i {index_type}
```

## Evaluation results

The results with the default parameters for Annoy, Faiss and NumpyIndexers are:

```bash
python app.py -t query -i numpy

Recall@100 => 99.47000050544739%
```

```bash
python app.py -t query -i faiss

Recall@100 => 47.16999990865588%
```

```bash
python app.py -t query -i annoy

Recall@100 => 77.69999986886978%
```

It can be good to look for different parameters to guarantee the best results

## Use Docker image from the jina hub

To make it easier for the user, we have built and published the [Docker image](https://hub.docker.com/r/jinahub/app.example.advancedvectorsearch) with the ANN_SIFT1M dataset indexed.
You can retrieve the docker image using:

```bash
docker pull jinahub/app.example.advancedvectorsearch:0.0.2-0.9.20
```
So you can pull from its latest tags. And you can run it. By default it runs the search with `faiss` indexer. 

To simply run it, please do:
```bash
docker run jinahub/app.example.advancedvectorsearch:0.0.2-0.9.20
```

If you want to run the image with `annoy` as a search library, you can override the entrypoint doing:

```bash
docker run -it --entrypoint=/bin/bash jinahub/app.example.advancedvectorsearch:0.0.2-0.9.20 entrypoint.sh annoy
```

If you want to change the parameters or of the `Faiss` or the `Annoy` Indexer you can pass different environment variables
to the `docker run` command by doing for instance:

```bash
docker run -e JINA_FAISS_INDEX_KEY='Flat' jinahub/app.example.advancedvectorsearch:0.0.2-0.9.20
```

An important parameter to set is `JINA_DISTANCE_REVERSE`, depending on the type of distance or metric that is used. For instance
for `inner_product` distance, `JINA_DISTANCE_REVERSE` should be set to True as the returned measure is similarity for `Faiss` and not
`distance`. Therefore the results should be scores in descending order.

Another parameter that cannot be found int the `init` arguments of `FaissIndexer` or `AnnoyIndexer` is `OMP_NUM_THREADS` that 
controls how many threads are used by `Faiss` when doing queries. Since the image has been built with 4 shards (around 250K documents each),
the `OMP_NUM_THREADS` is set to 1 by default to have the example use 4 CPUs. You can try to change also this parameter to investigate
the quality and speed of the results.


## Wrap up

In this example we have seen how to use different indexers as vector databases and how to use a `ref_indexer` as a base indexer.
 We also have seen how to use a pod inside a docker container inside our index and query flows, and how to use evaluators to assess the quality 
 of our search system.

## Next Steps

Where to go from here? You can always try:  

- different kinds of inverted indices and options from FAISS or Annoy.
- other indexers.
- indexing larger datasets.

Finally, play around with different evaluation metrics.

**Enjoy Coding with Jina!**

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
