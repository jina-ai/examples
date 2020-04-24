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


