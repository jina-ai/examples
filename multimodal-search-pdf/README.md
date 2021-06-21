
# PDF search with Jina

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

This example demonstrates how [Jina](http://www.jina.ai) can be used to search a repository of PDF files.  
The example employs a multimodal search architecture, allowing a user to query the data by providing text, or an image, or both simultaneously.

What's included in this example:

- Search text, image, PDF all in one Flow 
- Leverage Jina Recursive Document Representation to segment and encode text up to chunk-chunk level.
- Use customized executors to better fit your needs

## Data preparation

We have included several PDF blogs as toy data in [`toy_data`](toy_data).
This data is ready to use straight away. You can replace this toy data with your own by simply adding new files to the [`toy_data`](toy_data) folder. 
Be careful to check that the files are supported by [`pdfplumber`](https://github.com/jsvine/pdfplumber).

## Install

```bash
pip install wheel
pip install -r requirements.txt
```

## Run

| Command | Description |
| :--- | :--- |
| ``python app.py -t index`` | To index files/data |
| ``python app.py -t query_restful`` | To run a query Flow exposing a restful API (support search with image, text or PDFs) |
| ``python app.py -t query_text`` | To run a query Flow exposing a grpc interface (support search with text) |

## Start the Server

``` bash
python app.py -t index
python app.py -t query_text
```

## Query via REST API

When the REST gateway is enabled, Jina uses the [data URI scheme](https://en.wikipedia.org/wiki/Data_URI_scheme) to represent multimedia data. Simply organize your picture(s) into this scheme and send a POST request to `http://0.0.0.0:45670/api/search`, e.g.:

``` bash
curl --request POST -d '{"top_k": 10, "mode": "search",  "data": ["jina hello multimodal"]}' -H 'Content-Type: application/json' 'http://0.0.0.0:45678/search'
```
