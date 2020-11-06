
# Mocking IO and Use REST Gateway

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

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [WIP](#wip)
- [Available containers](#available-containers)
- [Build the app](#build-the-app)
- [Index local files of any type](#index-local-files-of-any-type)
- [Search](#search)
- [License](#license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


## WIP

## Available containers

- mocking `video/mp4`: `docker run -p 65481:65481 -e "JINA_PORT=65481" jinaai/hub.app.iomock.mp4 search`
- mocking `audio/wav`: `docker run -p 65481:65481 -e "JINA_PORT=65481" jinaai/hub.app.iomock.sound search`


## Build the app

With Python:

```bash
pip install --upgrade -r requirements.txt
```

In Docker:

```bash
docker build -t jinaai/hub.app.iomock .
```

## Index local files of any type

```bash
# index all python files
python app.py index '../**/*.py'

# index all mp4 files, recursively
python app.py index '/Users/hanxiao/Documents/**/*.mp4'

# index all pdf files under Document, non-recursive
python app.py index '/Users/hanxiao/Documents/*.pdf'
```

`'../**/*.py'` is the glob matching pattern. The index will be stored in `./workspace`.


or with Docker:

```bash
docker run -v "/Users/hanxiao/Documents/_jina/:/target:ro" -v "$(pwd)/workspace:/workspace" jinaai/hub.app.iomock index "target/**/*.py"
```

Not how we mount local files in read-only mode.

## Search

After index, you can now switch to the search mode:

```bash
python app.py search
```

or with Docker:

```bash
docker run -p 65481:65481 -e "JINA_PORT=65481" -v "$(pwd)/workspace:/workspace:ro" jinaai/hub.app.iomock search
```

where `"$(pwd)/workspace` is previously where your index stored.

Finally, you can query it via REST API:

```bash
curl -H "Origin: http://example.com" --verbose --request POST -d '{"top_k": 3, "data": ["data:image/png;base64,..."]}' -H 'Content-Type: application/json' 'http://0.0.0.0:59991/api/search'
```

It will return random results based on the number of queries and value of `top_k`

## License

Copyright (c) 2020 Jina AI Limited. All rights reserved.

Jina is licensed under the Apache License, Version 2.0. See [LICENSE](https://github.com/jina-ai/jina/blob/master/LICENSE) for the full license text.


