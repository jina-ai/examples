# Video Semantic Search in Scale with Prefetching and Sharding 

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

This tutorial shows how to use prefetching and sharding to improve the performance of your index and query flow. I assume you have already read [our entry-level tutorials](https://github.com/jina-ai/jina#getting-started). If you haven't, please do. I will go very fast on this one and  concentrate only on the prefetching and sharding. 

![Gif Video Search Demo](video-search-demo.gif)



<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Cotents**

- [Prerequirements](#prerequirements)
- [Run Index Flow](#run-index-flow)
- [Run Query Flow](#run-query-flow)
- [View the result in webpage](#view-the-result-in-webpage)
- [Prefetching](#prefetching)
- [Sharding](#sharding)
- [Documentation](#documentation)
- [Stay tuned](#stay-tuned)
- [License](#license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


## Prerequirements

```bash
pip install -r requirements.txt
```

### Download the data

```bash
python gif_download.py
```

There are quite some data, so you may want to modify this code or [the file list](data/tgif-v1.0.tsv) to get only part of them.


## Run Index Flow

Index flow is defined as follows:
```yaml
!Flow
with:
  logserver: true
pods:
  chunk_seg:
    yaml_path: craft/index-craft.yml
    replicas: $REPLICAS
    read_only: true
  doc_idx:
    yaml_path: index/doc.yml
  tf_encode:
    yaml_path: encode/encode.yml
    needs: chunk_seg
    replicas: $REPLICAS
    read_only: true
  chunk_idx:
    yaml_path: index/chunk.yml
    replicas: $SHARDS
    separated_workspace: true
  join_all:
    yaml_path: _merge
    needs: [doc_idx, chunk_idx]
    read_only: true
```

This breaks down into the following steps:
1. Segment each video into chunks;
2. Encode each chunk as a fixed-length vector;
3. Store all vector representations in a vector database with *shards*.

To run index:

```bash
python app.py
```


## Run Query Flow

Query flow is defined as follows:

```yaml
!Flow
with:
  logserver: true
  read_only: true  # better add this in the query time
pods:
  chunk_seg:
    yaml_path: craft/index-craft.yml
    replicas: $REPLICAS
  tf_encode:
    yaml_path: encode/encode.yml
    replicas: $REPLICAS
  chunk_idx:
    yaml_path: index/chunk.yml
    replicas: $SHARDS
    separated_workspace: true
    polling: all
    reducing_yaml_path: _merge_topk_chunks
    timeout_ready: 100000 # larger timeout as in query time will read all the data
  ranker:
    yaml_path: BiMatchRanker
  doc_idx:
    yaml_path: index/doc.yml
```

```bash
# change the Line 12 of app.py to 
# RUN_MODE = 'debug-query'
python app.py
```

The query flow breaks down into the following steps:
1. Do steps 1,2 in the index flow for each incoming query;
2. Retrieve relevant chunks from database;
3. Aggregate the chunk-level score back to document-level;
4. Return the top-k results to users.

## View the result in webpage

1. Copy `static` folder to the root of your workspace
2. Change the `modelID` in `vue-bindings.js`

    ```js
    const vm = new Vue({
        el: '#jina-ui',
        data: {
            serverUrl: './model/',
            modelId: '20200416085013',//'20191122144241',
            databasePath: '/topk.json',
        ...
        }
    ```

3. You may also need to change some paths. Just play with the javascript.
4. Host it like a static website, e.g. `python -m SimpleHTTPServer`.

I'm no expert on frontend and Vue. Feel free to contribute if you can improve it.

## Prefetching

Let's look at the `input_fn` of this demo,

```python
def input_fn(with_filename=True):
    idx = 0
    for g in glob.glob(GIF_BLOB)[:num_docs]:
        with open(g, 'rb') as fp:
            # print(f'im asking to read {idx}')
            if with_filename:
                yield g.encode() + b'JINA_DELIM' + fp.read()
            else:
                yield fp.read()
            idx += 1
```

What it does is reading all gif video files under `GIF_GLOB` and sending the binary contents to the Jina gateway one by one.

One natural question is why can't we send file path (i.e. a tiny binary string) to the gateway and parallelize the file reading inside Jina with multiple crafters?

If your data is stored on HDD, then multiple crafters can not improve the performance: the mechanical structure limits that only one "block" can be read/written at the same time. As your data files probably scatter all over the place, random read/write in parallel won't make significant difference in speed comparing to sequential reading.

If you use SSD, then such multi-reader implementation can indeed improve the performance. However, a further question is how many files can you load into Jina.

Think about a complete index workflow with crafters, encoders, and indexers, where encoders and indexers are often slower than crafters. If we don't add any restriction, `input_fn` will send all file paths to the gateway, which forces crafter to load **everything** into memory. As encoders and indexers can not consume data fast enough, your will soon run out of memory.

In Jina, we have two arguments `--prefetch` and `--prefetch-on-recv` in `gateway` to control the max number of pending requests in the network. If you see the log close enough, you will find:

```bash
           JINA@16221[W]:parser Client can not recognize the following args: ['--logserver', '--log-sse'], they are ignored. if you are using them from a global args (e.g. Flow), then please ignore this message
       PyClient@16221[S]:connected to the gateway at 0.0.0.0:54185!
index [=                   ] 📃      0 ⏱️ 0.0s 🐎 0.0/s      0 batchindex ...	        gateway@16221[I]:setting up sockets...
        gateway@16221[I]:input tcp://0.0.0.0:54179 (PULL_CONNECT) 	 output tcp://0.0.0.0:54136 (PUSH_CONNECT)	 control over ipc:///var/folders/hw/gpxkv2_n1fv0_cvxs6vjbc540000gn/T/tmpa2gl03i3 (PAIR_BIND)
        gateway@16221[I]:prefetching 50 requests...
        gateway@16221[W]:if this takes too long, you may want to take smaller "--prefetch" or ask client to reduce "--batch-size"
        gateway@16221[I]:prefetching 50 requests takes 22.588 secs
        gateway@16221[I]:send: 0 recv: 0 pending: 0
 chunk_seg-head@16239[I]:received "index" from gateway▸⚐
```

The `gateway` tells the client (`input_fn`) to send 50 requests before feeding to the first Pod of the flow. It stops there and takes some time (22s in the example above) to warm up. But after that you never have to wait such long time for IO ops again. This is because on every round-trip request, the gateway will tell the client to send `--prefetch-on-recv` number of new requests. If you use Dashboard to filter the log on `gateway` only, you can see that the whole Flow has always up to 50 requests in pending.

```bash
4/24/2020, 5:27:54 PM gateway@16335[I]: send: 0 recv: 0 pending: 0
4/24/2020, 5:28:57 PM gateway@16335[I]: send: 99 recv: 50 pending: 49
4/24/2020, 5:29:49 PM gateway@16335[I]: send: 149 recv: 100 pending: 49
```

This is good. Because on the one hand you avoid loading too many data into memory, on the other hand you still have enough data in memory to work with. With `--prefetch` turns on, the time of computation and IO operation are overlapped, make the whole flow non-blocking and highly efficient.

## Sharding

In this example, we set the number of `replicas` to 8 for `chunk_idx`. After indexing, when you open `workspace`, you will find:

```bash
.
 |-chunk_compound_indexer-8
 | |-vec.gz
 | |-chunk.gz
 | |-chunkidx.bin
 | |-vecidx.bin
 |-chunk_compound_indexer-6
 | |-vec.gz
 | |-chunk.gz
 | |-chunkidx.bin
 | |-vecidx.bin
 |-chunk_compound_indexer-1
 | |-vec.gz
 | |-chunk.gz
 | |-chunkidx.bin
 | |-vecidx.bin
 |-chunk_compound_indexer-7
 | |-vec.gz
 | |-chunk.gz
 | |-chunkidx.bin
 | |-vecidx.bin
 |-doc.gzip
 |-chunk_compound_indexer-2
 | |-vec.gz
 | |-chunk.gz
 | |-chunkidx.bin
 | |-vecidx.bin
 |-chunk_compound_indexer-5
 | |-vec.gz
 | |-chunk.gz
 | |-chunkidx.bin
 | |-vecidx.bin
 |-chunk_compound_indexer-4
 | |-vec.gz
 | |-chunk.gz
 | |-chunkidx.bin
 | |-vecidx.bin
 |-chunk_compound_indexer-3
 | |-vec.gz
 | |-chunk.gz
 | |-chunkidx.bin
 | |-vecidx.bin
 |-doc_indexer.bin
```

You can see that the data is splitted into 8 different directories under the given `workspace`, in a more or less uniform way. This is good because otherwise we end up with one big file that is slow to load and to query. With sharding enabled, one can query multiple smaller index in parallel, which gives better efficiency. 

If you think about it, a multi-replica indexer behaves no differently than a multi-replica crafter/encoder at least in the index time: replicas compete for every incoming request and each request eventually is polled by one replica. The only difference is that multi-replica crafter/encoder is usually stateless and does not need independent workspace. However, each indexer replica needs a separate workspace to distinguish their own data from others. Hence, for `chunk_idx`, we set `separated_workspace` to `true`. Each replica works in its own sub-workspace. For this reason, we call **Replica** with `separated_workspace=True` as **Shard**.

In the query time, replicas and shards behave differently on how they handle new requests. Replicas still compete on each request as they do in the index time. Shards, however, work more cooperatively: each request is published to *all* replicas, each replica works on the same request, and the final result has to be collected from all replicas.

In Jina, such behavior in the query time can be simply specified via `polling` and `reducing_yaml_path`:

```yaml
    polling: all
    reducing_yaml_path: _merge_topk_chunks
```

`polling` and `reducing_yaml_path` are Pod-specific argument, you can find more details in `jina pod --help`.

```bash
--polling {ANY, ALL, ALL_ASYNC}
    ANY: only one (whoever is idle) replica polls the message; 
    ALL: all workers poll the message (like a broadcast) 
    (choose from: {ANY, ALL, ALL_ASYNC}; default: ANY)
    
--reducing-yaml-path
    the executor used for reducing the result from all replicas, accepted type follows "--yaml-path"
    (type: str; default: _forward)
```

When running `app.py` for query, you will see from the log that these 8 shards are working together:

```bash
 chunk_idx-head@17648[I]:received "search" from gateway▸chunk_seg▸tf_encode▸⚐
 chunk_idx-tail@17649[I]:received "search" from gateway▸chunk_seg▸tf_encode▸chunk_idx-head▸chunk_idx-8▸⚐
    chunk_idx-8@17657[I]:received "search" from gateway▸chunk_seg▸tf_encode▸chunk_idx-head▸⚐
    chunk_idx-7@17656[I]:received "search" from gateway▸chunk_seg▸tf_encode▸chunk_idx-head▸⚐
 chunk_idx-tail@17649[I]:received "search" from gateway▸chunk_seg▸tf_encode▸chunk_idx-head▸chunk_idx-7▸⚐
      chunk_seg@17642[I]:received "search" from gateway▸⚐
 chunk_idx-tail@17649[I]:received "search" from gateway▸chunk_seg▸tf_encode▸chunk_idx-head▸chunk_idx-1▸⚐
    chunk_idx-1@17650[I]:received "search" from gateway▸chunk_seg▸tf_encode▸chunk_idx-head▸⚐
 chunk_idx-tail@17649[I]:received "search" from gateway▸chunk_seg▸tf_encode▸chunk_idx-head▸chunk_idx-6▸⚐
    chunk_idx-6@17655[I]:received "search" from gateway▸chunk_seg▸tf_encode▸chunk_idx-head▸⚐
 chunk_idx-tail@17649[I]:received "search" from gateway▸chunk_seg▸tf_encode▸chunk_idx-head▸chunk_idx-5▸⚐
    chunk_idx-5@17654[I]:received "search" from gateway▸chunk_seg▸tf_encode▸chunk_idx-head▸⚐
    chunk_idx-3@17652[I]:received "search" from gateway▸chunk_seg▸tf_encode▸chunk_idx-head▸⚐
 chunk_idx-tail@17649[I]:received "search" from gateway▸chunk_seg▸tf_encode▸chunk_idx-head▸chunk_idx-3▸⚐
 chunk_idx-tail@17649[I]:received "search" from gateway▸chunk_seg▸tf_encode▸chunk_idx-head▸chunk_idx-4▸⚐
    chunk_idx-4@17653[I]:received "search" from gateway▸chunk_seg▸tf_encode▸chunk_idx-head▸⚐
 chunk_idx-tail@17649[I]:received "search" from gateway▸chunk_seg▸tf_encode▸chunk_idx-head▸chunk_idx-2▸⚐
 chunk_idx-tail@17649[I]:collected 8/8 parts of SearchRequest
    chunk_idx-2@17651[I]:received "search" from gateway▸chunk_seg▸tf_encode▸chunk_idx-head▸⚐
 chunk_idx-head@17648[I]:received "search" from gateway▸chunk_seg▸tf_encode▸⚐
      tf_encode@17643[I]:received "search" from gateway▸chunk_seg▸⚐
      chunk_seg@17642[I]:received "search" from gateway▸⚐
         ranker@17659[I]:received "search" from gateway▸chunk_seg▸tf_encode▸chunk_idx-head▸chunk_idx-2▸chunk_idx-1▸chunk_idx-6▸chunk_idx-5▸chunk_idx-8▸chunk_idx-3▸chunk_idx-7▸chunk_idx-4▸chunk_idx-tail▸⚐
```

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
