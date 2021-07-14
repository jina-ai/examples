
# Lyrics Search: Understanding Chunks

[![Jina](https://github.com/jina-ai/jina/blob/master/.github/badges/jina-badge.svg?raw=true  "We fully commit to open-source")](https://get.jina.ai)

[![](demo.gif)](https://www.youtube.com/watch?v=GzufeV8AY_w)

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Dataset](#dataset)
- [[Optional] Download full lyrics dataset](#optional-download-full-lyrics-dataset)
- [Install](#install)
- [Run](#run)
- [View in Browser](#view-in-browser)
- [License](#license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


## Dataset

The dataset used in this example contains lyrics of songs.

We have included 1000 songs' lyrics as toy data in [`lyrics-data`](lyrics-data).
This data is ready to use with this example.

### [Optional] Download full lyrics dataset

If you want to use the full dataset, you can download it from kaggle (https://www.kaggle.com/neisse/scrapped-lyrics-from-6-genres).
To get it, once you have your Kaggle Token in your system as described in (https://www.kaggle.com/docs/api), run:

```bash
bash get_data.sh
```

## Installation

```bash
pip install -r requirements.txt
```

## Command Overview

| Command | Description |
| :--- | :--- |
| ``python app.py -t index`` | To index the dataset |
| ``python app.py -t query`` | Start a REST API working on queries |
| ``python app.py -t query_text`` | Perform one query with your custom text |

Then, open `http://0.0.0.0:8000/` in your browser.

## 🏃 Run the Flows
Now that we've got the code to load our data, we're going to dive into writing our app and running our Flows!
### Index Flow
To run the index you type:
```bash
python app.py -t index
```
First up we need to build up an index and then search through this index when we use the query Flow later.
Then we have ready all the indexes!
### Query Flow
Now for the query time, run:
```bash
python app.py -t query
```
This starts an API waiting for query requests.  
You can send a query using cURL:
```sh
curl --request POST -d '{"parameters": {"top_k": 10}, "data": ["hello world"]}' -H 'Content-Type: application/json' 'http://0.0.0.0:45678/search'
````
Alternatively, use the provided frontend:
```bash
cd static
python -m http.server
```
Then, open `http://0.0.0.0:8000/` in your browser.
## License

Copyright (c) 2020-2021 Jina AI. All rights reserved.
