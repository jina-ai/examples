# Semantic Wikipedia Search with Transformers and DistilBERT

![](https://docs.jina.ai/_images/jinabox-wikipedia.gif)

| item   | content                                          |
|--------|--------------------------------------------------|
| Input  | 1 text file with 1 sentence per line             |
| Output | *top_k* number of sentences that match input query |

This is an example of using [Jina](http://www.jina.ai)'s neural search framework to search through a [selection of individual Wikipedia sentences](https://www.kaggle.com/mikeortman/wikipedia-sentences) downloaded from Kaggle. It uses the [`distilbert-based-uncased`](https://huggingface.co/distilbert-base-uncased) language model from [Transformers](https://huggingface.co).

## 🐍 Setup

```sh
pip install -r requirements.txt
```

## 📇 Index

We'll start off by indexing a [small dataset of 50 sentences](data/toy-input.txt) to make sure everything is working:

```sh
python app.py -t index
```

To index the [full dataset](https://www.kaggle.com/mikeortman/wikipedia-sentences) (almost 900 MB):

1. Set up [Kaggle](https://www.kaggle.com/docs/api#getting-started-installation-&-authentication)
2. Run the script: `sh ./get_data.sh`
3. Set the input file: `export JINA_DATA_FILE='data/input.txt'`
4. Set the number of docs to index `export JINA_MAX_DOCS=30000` (or whatever number you prefer. The default is `50`)
5. Delete the old index: `rm -rf workspace`
6. Index your new dataset: `python app.py -t index`

If you are using a subset of the data (less then 30,000 documents) we recommend you shuffle the data. This is because the input file is ordered alphabetically, and Jina indexes from the top down. So without shuffling, your index may contain unrepresentative data, like this:

```
0.000123, which corresponds to a distance of 705 Mly, or 216 Mpc.
000webhost is a free web hosting service, operated by Hostinger.
0010x0010 is a Dutch-born audiovisual artist, currently living in Los Angeles.
0-0-1-3 is an alcohol abuse prevention program developed in 2004 at Francis E. Warren Air Force Base based on research by the National Institute on Alcohol Abuse and Alcoholism regarding binge drinking in college students.
0.01 is the debut studio album of H3llb3nt, released on February 20, 1996 by Fifth Colvmn Records.
001 of 3 February 1997, which was signed between the Government of the Republic of Rwanda, and FAPADER.
003230 is a South Korean food manufacturer.
```

On Linux, you can shuffle using the [`shuf` command](https://linuxhint.com/bash_shuf_command/):

```bash
shuf input.txt > input.txt
```

To shuffle a file on macos, please read [this post](https://apple.stackexchange.com/questions/142860/install-shuf-on-os-x/195387).

## 🔍 Search

### With REST API

```sh
python app.py -t query_restful
```

Then:

```sh
curl --request POST -d '{"top_k": 10, "mode": "search",  "data": ["hello world"]}' -H 'Content-Type: application/json' 'http://0.0.0.0:45678/search'
````

Or use [Jinabox](https://jina.ai/jinabox.js/) with endpoint `http://127.0.0.1:45678/search`

### From the Terminal

```sh
python app.py -t query
```

### Next Steps

- [Enable incremental indexing](https://github.com/jina-ai/examples/tree/master/wikipedia-sentences/README.incremental.md)
- [Developer Guide: Build a similar text search app](https://docs.jina.ai/chapters/my_first_jina_app/)


## 🚧[NO LONGER MAINTAINED]🐳 Run in Docker

To test this example you can run a Docker image with 30,000 pre-indexed sentences:

```sh
docker run -p 45678:45678 jinahub/app.example.wikipedia-sentences-30k:0.2.10-1.0.10
```

You can then query by running:

```sh
curl --request POST -d '{"top_k": 10, "mode": "search",  "data": ["hello world"]}' -H 'Content-Type: application/json' 'http://0.0.0.0:45678/api/search'
```

