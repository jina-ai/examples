<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Jina ❤️ Docker and RESTful APIs](#jina--docker-and-restful-apis)
  - [Run the Docker](#run-the-docker)
  - [Index and Search By Yourself](#index-and-search-by-yourself)
  - [Next Steps](#next-steps)
  - [Documentation](#documentation)
  - [Stay tuned](#stay-tuned)
  - [License](#license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Jina ❤️ Docker and RESTful APIs

## Run the Docker

We have put the south park example in a Docker image and make it ready to search. 

```bash
docker run -p 45678:45678 jinaai/hub.app.distilbert-southpark:latest
```

Now you can check out the results via HTTP POST request. Jina supports RESTful APIs, and you can simply send a POST request to `http://0.0.0.0:45678/api/search`, e.g.

```bash
curl --request POST \
     -d '{"top_k": 10, "mode": "search",  "data": ["text:You are damn right"]}' \
     -H 'Content-Type: application/json' \
     'http://0.0.0.0:45678/api/search'
```

You can find more details of the Jina RESTful APIs at [docs](https://docs.jina.ai/chapters/restapi/#interface).

The response is organized in the format of `json` and the matched results is stored in `topkResults`.


<details>
<summary>Click here to see the console output</summary>

```
{
  "search": {
    "docs": [
      {
        "weight": 1.0,
        "length": 1,
        "topkResults": [
          {
            "matchDoc": {
              "docId": 9328,
              "weight": 1.0,
              "mimeType": "text/plain",
              "text": "Stan[SEP]Oh thanks, dude.\n"
            },
            "score": {
              "value": 0.2900288,
              "opName": "MinRanker"
            }
          },
          {
            "matchDoc": {
              "docId": 7600,
              "weight": 1.0,
              "mimeType": "text/plain",
              "text": "StephenAbootman[SEP]Don't call me your guy!\n"
            },
            "score": {
              "value": 0.28131312,
              "opName": "MinRanker"
            }
          },
          {
            "matchDoc": {
              "docId": 7497,
              "weight": 1.0,
              "mimeType": "text/plain",
              "text": "MrNelson[SEP]Excuse me: over here, please?\n"
            },
            "score": {
              "value": 0.2740146,
              "opName": "MinRanker"
            }
          },
          {
            "matchDoc": {
              "docId": 8814,
              "weight": 1.0,
              "mimeType": "text/plain",
              "text": "Kyle[SEP]Thanks, dude.\n"
            },
            "score": {
              "value": 0.27255633,
              "opName": "MinRanker"
            }
          },
          {
            "matchDoc": {
              "docId": 9957,
              "weight": 1.0,
              "mimeType": "text/plain",
              "text": "Kyle[SEP]Thanks, dude!\n"
            },
            "score": {
              "value": 0.27255633,
              "opName": "MinRanker"
            }
          },
          {
            "matchDoc": {
              "docId": 7868,
              "weight": 1.0,
              "mimeType": "text/plain",
              "text": "Token[SEP]Thanks, dude.\n"
            },
            "score": {
              "value": 0.27255633,
              "opName": "MinRanker"
            }
          },
          {
            "matchDoc": {
              "docId": 239,
              "weight": 1.0,
              "mimeType": "text/plain",
              "text": "Randy[SEP]Hey, it's my boss.\n"
            },
            "score": {
              "value": 0.27224803,
              "opName": "MinRanker"
            }
          },
          {
            "matchDoc": {
              "docId": 5389,
              "weight": 1.0,
              "mimeType": "text/plain",
              "text": "Cartman[SEP]I got your time phone!\n"
            },
            "score": {
              "value": 0.2721367,
              "opName": "MinRanker"
            }
          },
          {
            "matchDoc": {
              "docId": 5878,
              "weight": 1.0,
              "mimeType": "text/plain",
              "text": "Kyle[SEP]Wow, dude, check it out!\n"
            },
            "score": {
              "value": 0.2709449,
              "opName": "MinRanker"
            }
          },
          {
            "matchDoc": {
              "docId": 4388,
              "weight": 1.0,
              "mimeType": "text/plain",
              "text": "Steve[SEP]Please hang on, I'm going to call Customer Service.\n"
            },
            "score": {
              "value": 0.27075276,
              "opName": "MinRanker"
            }
          }
        ],
        "mimeType": "text/plain",
        "text": "text:hey, dude"
      }
    ],
    "topK": 10
  }
}
```
</details>

## Index and Search By Yourself

### Index

You can give it a try and index the data by yourself as well. We've built another docker image for playing around. 

```bash
docker run -v "$(pwd)/workspace:/workspace" -v "$(pwd)/data:/data" -e "JINA_LOG_PROFILING=1" -p 5000:5000 -e "MAX_NUM_DOCS=100" jinaai/hub.app.distilbert index
```

**Command args explained**

- `$(pwd)/data` is the path of the data, running `bash get_data.sh` will store the data at `$(pwd)/data` by default
- `$(pwd)/workspace` is where the Jina index will be stored.
- `-e "JINA_LOG_PROFILING=1" -p 5000:5000` are just for dashboard monitoring. They are optional. By setting these args, you can monitor the logs at [Jina dashboard](https://dashboard.jina.ai/#/logs). 
- `-e "MAX_NUM_DOCS=100"` is to set up the maximal number of documents to stored. For illustation purpose, we set it to `100`.


### Search

After building the index, you can use the following command to search,

```bash
docker run -v "$(pwd)/workspace:/workspace" -p 45678:45678 jinaai/hub.app.distilbert search
```

**Command args explained**

- `$(pwd)/workspace` is where the Jina index will be stored.
- `-p 45678:45678` is for mapping the RESTful APIs to the local machine.

Now you can search with the RESTful APIs as before.


### Index your own data
Of course, you can use this docker image to index your own data as well. Simply save your text data at `/your/favourite/path` with the name `my_awesome_data.csv` and keep each Document you want to index at one line in that file. Run the following command,

```bash
docker run -v "$(pwd)/workspace:/workspace" -v "/your/favourite/path:/data" -e "DATA_FILE= my_awesome_data.csv" jinaai/hub.app.distilbert index

```

## Next Steps
- Check out the details of this demo at [README.md](../README.md)

## Documentation

<a href="https://docs.jina.ai/">
<img align="right" width="350px" src="https://github.com/jina-ai/jina/blob/master/.github/jina-docs.png" />
</a>

The best way to learn Jina in depth is to read our documentation. Documentation is built on every push, merge, and release event of the master branch. You can find more details about the following topics in our documentation.

- [Jina command line interface arguments explained](https://docs.jina.ai/chapters/cli/index.html)
- [Jina Python API interface](https://docs.jina.ai/api/jina.html)
- [Jina YAML syntax for executor, driver and flow](https://docs.jina.ai/chapters/yaml/yaml.html)
- [Jina Protobuf schema](https://docs.jina.ai/chapters/proto/index.html)
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




