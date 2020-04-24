# Video Semantic Search in Scale with Prefetching and Sharding 

This tutorial shows how to use prefetching and sharding to improve the performance of your index and query flow. I assume you have already read [our entry-level tutorials](https://github.com/jina-ai/jina#getting-started). If you haven't, please do. I will go very fast on this one and  concentrate only on the prefetching and sharding. 

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
1. segment each video into chunks;
2. encode each chunk as a fixed-length vector;
3. store all vector representations in a vector database with *shards*.

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
1. do steps 1,2 in the index flow for each incoming query;
2. retrieve relevant chunks from database;
3. aggregate the chunk-level score back to document-level;
4. return the top-k results to users.


## Prefetching

Let's look at the `input_fn` of this demo,

```python
def input_fn(random=False, with_filename=True):
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

If your data is stored on HDD, then multiple crafters can not improve the performance: the mechanical structure restricts that only one "block" can be read/written at the same time. As your data file probably scatters all over the place, random read/write in parallel won't make any difference in speed comparing to reading them one by one.

If you use SSD, then such implementation can indeed improve the performance. However, a further question is how many files can you load into Jina.

Think about a complete index workflow with crafters and encoders, indexers, where encoders and indexers are often slower than crafters. If we don't add any restriction, `input_fn` will send all file paths to the gateway, which forces crafter to load **everything** into memory. As encoders and indexers can not consume data fast enough, your will soon run out of memory.

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

This is good. Because on the one hand you avoid loading too many data into memory, on the other hand you still have enough data in memory to work with. With `--prefetch` turns on, the time of computation and IO operation are overlapped, make the whole flow highly efficient.

