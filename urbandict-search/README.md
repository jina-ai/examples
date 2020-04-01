# urbandict-search

This demo shows how to use Jina to build a text search engine.

We use the [urban-dictionary-words-dataset](https://www.kaggle.com/therohk/urban-dictionary-words-dataset) as an example. The data contains 2.5 million phrases from Urban Dictionary with definations and votes. 

In this demo, we consider each word with its definations as one **document**. As a common practic in Jina, each documents are represented by **chunks**. Here we consider each defination as one chunk, and use the embeddings of each defination to index. Some words have more than one definations from different users. In such cases, we use the ratio between upvotes and downvotes as the **weight of the chunks**.

## Prerequirements

This demo requires Python 3.7.

```bash
pip install -r requirements.txt
```

You also need to have Jina installed, please refer to [the installation guide](https://github.com/jina-ai/jina#getting-started), in particular following [the recommended way for developers](https://github.com/jina-ai/jina#dev-mode-install-from-your-local-folkclone).

Download the data from
[https://www.kaggle.com/therohk/urban-dictionary-words-dataset](https://www.kaggle.com/therohk/urban-dictionary-words-dataset) and saved at `/tmp`

## Prepare the data
We download the data from [https://www.kaggle.com/therohk/urban-dictionary-words-dataset](https://www.kaggle.com/therohk/urban-dictionary-words-dataset) and keep the first 100 rows as queries.

```bash
python prepare_data.py
head -n 100 /tmp/jina/urbandict/urbandict-word-defs.csv > /tmp/jina/urbandict/query.csv
```

## Run Index

```bash
python index.py
```

The indices are saved at `/tmp/jina/urbandict/`.


## Run Query
The query results are saved in `/tmp/jina/urbandict/query_result.json`

```bash
python query.py
```