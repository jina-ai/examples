# Add Incremental Indexing to Wikipedia Search

<table>
  <tr>
    <td>
      Input
    </td>
    <td>
      2 text files with 1 sentence per line
    </td>
  </tr>
  <tr>
    <td>
      Output
    </td>
    <td>
      top_k number of sentences that match input query
    </td>
  </tr>
</table>

This is an example of using [Jina](http://www.jina.ai)'s neural search framework to add incremental indexing to our [Wikipedia sentence search example](https://github.com/jina-ai/examples/tree/master/wikipedia-sentences)

## Prerequisites

- Run and understand our [Wikipedia sentence search example](https://github.com/jina-ai/examples/tree/master/wikipedia-sentences)

## What is incremental indexing?

Briefly, this lets a user re-use an index to add new data. It also automatically adds documents with duplicate IDs. For a more in-depth explanation on how Jina handles this, refer to [our documentation](https://docs.jina.ai/chapters/prevent_duplicate_indexing/index.html).

## Configuration changes

In order to adapt the Wikipedia sentence search example to support incremental indexing, we need to:

### Edit Flows

Change `indexer` entry in `flows/index.yml` and `flows/query.yml` to use `DocCache` as a filter (in the `uses_before` field). This ensures that we prevent duplicates.

In this example the `DocCache` is separated into its own `.yml` file, in `pods/index_cache.yml`:

```yaml
!DocCache
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

This might look complicated, but it basically first checks the cache for any matching doc IDs before indexing and querying.

### Adapt Dataset

We split the dataset into two files: `input-1.txt` and `input-2.txt`. This way we can index one, close the `Flow` object, and then index the other.

The environment variable `JINA_DATA_FILE` has also been split, with `JINA_DATA_FILE_1` and `JINA_DATA_FILE_2` pointing to the two files above.

### Adapt `app.py`

Adapt `app.py` to index, close, and index again.

When running `python app.py -t index` we would usually only index one file. We now have the following:

```python
f = Flow().load_config("flows/index.yml")

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

## Run in Docker

To test this example you can run a Docker image which will index both data files then enter query mode:

```sh
docker run -p 45678:45678 jinahub/app.example.wikipedia-sentences-incremental:0.1-0.9.24
```

You can then query by running:

```sh
curl --request POST -d '{"top_k": 10, "mode": "search",  "data": ["text:hello world"]}' -H 'Content-Type: application/json' 'http://0.0.0.0:45678/api/search'`
```
