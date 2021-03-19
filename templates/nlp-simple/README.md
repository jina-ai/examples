# Jina NLP App Template

## Important note

This example **isn't supposed to work as is**. It's meant as a template for users to fill in their own data. This helps them build a Jina NLP search app from scratch, as in [My First Jina App](https://docs.jina.ai/chapters/my_first_jina_app.html).

## What this template includes

- Sample indexing and query Flows
- Sample Pods
- Tests with placeholder strings
- An empty shell script for getting remote dataset
- Dockerfile
- Support files (requirements.txt, manifest.json, etc)

## Setup

```sh
pip install -r requirements.txt
```

## Index

As mentioned above, you'll need to provide your own data file under `data/input.txt` (or specify with `JINA_DATA_FILE` environment variable).

```sh
python app.py -t index
```

## Search

### With REST API

To start the Jina server:

```sh
python app.py -t query_restful
```

Then use a client to query:

```sh
curl --request POST -d '{"top_k": 10, "mode": "search",  "data": ["hello world"]}' -H 'Content-Type: application/json' 'http://0.0.0.0:45678/api/search'
````

Or use [Jinabox](https://jina.ai/jinabox.js/) with endpoint `http://127.0.0.1:45678/api/search`

### From the terminal

```sh
python app.py -t query
```

## Build a Docker image

This will create a Docker image with pre-indexed data and an open port for REST queries.

1. Run all the steps in setup and index first. Don't run anything in the search step!
2. If you want to [push to Jina Hub](#push-to-jina-hub) be sure to edit the `LABEL`s in `Dockerfile` and fields in `manifest.yml` to avoid clashing with other images
3. Run `docker build -t <your_image_name> .` in the root directory of this repo
5. Run it with `docker run -p 45678:45678 <your_image_name>`
6. Search using instructions from [Search section](#search) above

### Image name format

Please use the following name format for your Docker image, otherwise it will be rejected if you want to push it to Jina Hub. 

```
jinahub/type.kind.image-name:image-version-jina_version
```

For example:

```
jinahub/app.example.my-wikipedia-sentences-30k:0.2.9-1.0.1
```

## Push to [Jina Hub](https://github.com/jina-ai/jina-hub)

1. Ensure hub is installed with `pip install jina[hub]`
2. Run `jina hub login` and paste the code into your browser to authenticate
3. Run `jina hub push <your_image_name>`
