# Flow API Tutorial 
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

In this demo, we'll use some code snippets to show you how to use flow API for indexing/searching different data. Make sure you've gone through [Jina 101](https://github.com/jina-ai/jina/tree/master/docs/chapters/101) and understood the Pod, Flow, Yaml before moving on. 

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Overview](#overview)
- [3 APIs for indexing your data](#3-APIs-for-indexing-your-data)
    - [index_ndarray API](#1-index_ndarray-api)
    - [index_files API](#2-index_files-api)
    - [index_lines API](#3-index_lines-api)
- [3 APIs for searching your data](#3-APIs-for-searching-your-data)
    - [search_ndarray API](#1-search_ndarray-api)
    - [search_files API](#2-search_files-api)
    - [search_lines API](#3-search_lines-api)
- [Wrap up](#wrap-up)
- [Next Steps](#next-steps)
- [Documentation](#documentation)
- [Community](#community)
- [License](#license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->
## Overview
Jina supports you to index/search your data in a simple way. And it exposes 3 APIs for each of them, which help you to index or search `ndarray`, `files`, and `lines` data.

## 3 APIs for indexing your data

### 1. index_ndarray API
`index_ndarray()` is the API for indexing `ndarray`. 

```python
import numpy as np
from jina.flow import Flow
input_data = np.random.random((3,8))
f = Flow().add(uses='_logforward')
with f:
    f.index_ndarray(input_data)
```
    
#### Let's explain it line by line
    
* Firstly, import `numpy` to generate input data. 
* Secondly, import `Flow` from `jina.flow`, which provides flow API. 
* Thirdly, a 3*8 random matrix by numpy is created as input data. 
* Fourthly, add an empty pod named `_logforward` to the Flow. [`_logforward`](https://docs.jina.ai/chapters/simple_exec.html) is a built-in yaml, which just forwards input data to the results, and it locates in `jina/resources/executors._forward.yml`. You can also use your own [yaml](https://docs.jina.ai/chapters/yaml/yaml.html) to organize `pods`.
* Use `with f:` to recycle the computer resources automatically.
* At last, start the Flow by using API `index_ndarray()`. The results will be printed in the logs. 
#### Let's dive into the logs
```protobuf
envelope {
  receiver_id: "7b6015cb12"
  request_id: 1
  timeout: 5000
  routes {
    pod: "gateway"
    pod_id: "7b6015cb12"
    start_time {
      seconds: 1597931714
      nanos: 343076000
    }
  }
  routes {
    pod: "pod0"
    pod_id: "9cdca90c5a"
    start_time {
      seconds: 1597931714
      nanos: 347768000
    }
  }
  version {
    jina: "0.4.1"
    proto: "0.0.55"
  }
  num_part: 1
}
request {
  request_id: 1
  index {
    docs {
      id: 1
      weight: 1.0
      length: 100
      blob {
        buffer: "\004@\316\362/D\333?\244>\235\305\027\311\336?\267\210\251\311^\260\345?\366\n(\014\022m\356?\374\262\017\030\036\357\351?-c\300\337\217V\345?\241G\241\352\233\024\356?\340\346lUf\353\350?"
        shape: 8
        dtype: "float64"
      }
    }
    docs {
      id: 2
      weight: 1.0
      length: 100
      blob {
        buffer: "\312Wm\337\250\217\354?t\212\326\020\261\r\320?\254\262\300u<O\323?\340\210\222$\321\216\314?\310.q,+\347\311?&\316\361\310\252R\331?\214\016\201a\231\262\330?\342\231\262\221\343%\324?"
        shape: 8
        dtype: "float64"
      }
    }
    docs {
      id: 3
      weight: 1.0
      length: 100
      blob {
        buffer: "kT\250\372K%\345?\237\017+u\300\227\353?\3668\256\340\251\227\350?\327\006$\032$\002\341?\274\300\3573\371\262\343?\346\371\265dV\330\342?\370\210\360\002P3\340?\022i-\016\374\320\331?"
        shape: 8
        dtype: "float64"
      }
    }
  }
}
```
Printed in the log, Flow formatted the input data by `jina.proto`, which is a [protobuf](https://docs.jina.ai/chapters/proto/docs.html) file. Pods forward the structured input data to each other or to the clients by [gRPC](https://docs.jina.ai/chapters/restapi/index.html?highlight=grpc).

`envelope` and `request` are the top of the log structure. `envelope` includes some metadata and control data. `request` contains input data and related metadata. A 3*8 matrix was sent to the Flow as an input. which matches 3 `request.index.docs`, and the `request.index.docs.blog.shape` is 8. The vector of the matrix is stored in `request.index.docs.blob`, and the `request.index.docs.blob.dtype` indicates the type of the vector.

### 2. index_files API
`index_files()` is the API for indexing `files` 

```python
from jina.flow import Flow
f = Flow().add(uses='_logforward')
with f:
    f.index_files(f'../pokedex-with-bit/pods/*.yml')
```
#### Let's explain the main part in code snippets and logs
API `index_files()` reads input data from `../pokedex-with-bit/pods/*.yml`. In this directory, there are 5 yaml files. As a result, you can find 5 `request.index.docs` in the log, and the paths of the 5 files stores in `request.index.docs.uri`. Please refer to [index_ndarray()](#1-index_ndarray-api) for more information.
```protobuf
envelope {
  receiver_id: "4c5eff0d35"
  request_id: 1
  timeout: 5000
  routes {
    pod: "gateway"
    pod_id: "4c5eff0d35"
    start_time {
      seconds: 1597935647
      nanos: 100468000
    }
  }
  routes {
    pod: "pod0"
    pod_id: "b387944ecf"
    start_time {
      seconds: 1597935647
      nanos: 104758000
    }
  }
  version {
    jina: "0.4.1"
    proto: "0.0.55"
  }
  num_part: 1
}
request {
  request_id: 1
  index {
    docs {
      id: 1
      weight: 1.0
      length: 100
      uri: "../pokedex-with-bit/pods/encode-baseline.yml"
    }
    docs {
      id: 2
      weight: 1.0
      length: 100
      uri: "../pokedex-with-bit/pods/chunk.yml"
    }
    docs {
      id: 3
      weight: 1.0
      length: 100
      uri: "../pokedex-with-bit/pods/doc.yml"
    }
    docs {
      id: 4
      weight: 1.0
      length: 100
      uri: "../pokedex-with-bit/pods/encode.yml"
    }
    docs {
      id: 5
      weight: 1.0
      length: 100
      uri: "../pokedex-with-bit/pods/craft.yml"
    }
  }
}
```
### 3. index_lines API
`index_lines()` is the API for indexing `lines`. 
```python
from jina.flow import Flow
input_str = ['aaa','bbb']
f = Flow().add(uses='_logforward')
with f:
    f.index_lines(lines=input_str)
``` 
#### Let's explain the main part in code snippets and logs
API `index_lines()` reads input data from `input_str`. There are 2 elements in the `input_str`. As a result, you can find 2 `request.index.docs` in the log, and the input data stores in `request.index.docs.text`. Please refer to [index_ndarray API](#1-index_ndarray-api) for more information.

```protobuf
envelope {
  receiver_id: "e3c2f8ea9c"
  request_id: 1
  timeout: 5000
  routes {
    pod: "gateway"
    pod_id: "e3c2f8ea9c"
    start_time {
      seconds: 1597937249
      nanos: 486299000
    }
  }
  routes {
    pod: "pod0"
    pod_id: "67c4660afe"
    start_time {
      seconds: 1597937249
      nanos: 490460000
    }
  }
  version {
    jina: "0.4.1"
    proto: "0.0.55"
  }
  num_part: 1
}
request {
  request_id: 1
  index {
    docs {
      id: 1
      weight: 1.0
      length: 100
      mime_type: "text/plain"
      text: "aaa"
    }
    docs {
      id: 2
      weight: 1.0
      length: 100
      mime_type: "text/plain"
      text: "bbb"
    }
  }
}
```

## 3 APIs for searching your data

### 1. search_ndarray API
`search_ndarray()` is the API for searching `ndarray`. 
```python
import numpy as np
from jina.flow import Flow
input_data = np.random.random((3,8))
f = Flow().add(uses='_logforward')
with f:
   f.search_ndarray(input_data)
```
The steps and logs are quite the same as [index_ndarray API](#1-index_ndarray-api), the main difference is that `request.index` is replaced by `request.search`
### 2. search_files API
`search_files()` is the API for searching `files`. 
```python
from jina.flow import Flow
f = Flow().add(uses='_logforward')
with f:
    f.search_files(f'../pokedex-with-bit/pods/chunk.yml')
```
The steps and logs are quite the same as [index_files API](#2-index_files-api), the main difference is that `request.index` is replaced by `request.search`
### 3. search_lines API
`search_lines()` is the API for searching `lines`. 
```python
from jina.flow import Flow
text = input('please type a sentence: ')
f = Flow().add(uses='_logforward')
with f:   
    f.search_lines(lines=[text, ])
```
The steps and logs are quite the same as [index_lines API](#3-index_lines-api), the main difference is that `request.index` is replaced by `request.search`
## Wrap up
In this example, we showed you how to use `index` and `search` API in a `flow`, and described the data structure in `flow` procedure.

## Next Steps

- Write your own Flows.
- try more examples on `index` and `search`

| APIs | Links  |
| --- | --- |
|`ndarray` | [Faiss Search](https://github.com/jina-ai/examples/tree/master/faiss-search) |
|`files`  |[Flower Search](https://github.com/jina-ai/examples/tree/master/flower-search)|
|`lines` | [Southpark Search](https://github.com/jina-ai/examples/tree/master/southpark-search) |
<!---
- Check out the Docker images at Jina hub. 
--->

## Documentation 

<a href="https://docs.jina.ai/">
<img align="right" width="350px" src="https://github.com/jina-ai/jina/blob/master/.github/jina-docs.png" />
</a>

The best way to learn Jina in-depth is to read our documentation. Documentation is built on every push, merge, and release event of the master branch. For more details, check out:

- [Jina command line interface arguments explained](https://docs.jina.ai/chapters/cli/index.html)
- [Jina Python API interface](https://docs.jina.ai/api/jina.html)
- [Jina YAML syntax for executor, driver and flow](https://docs.jina.ai/chapters/yaml/yaml.html)
- [Jina Protobuf schema](https://docs.jina.ai/chapters/proto/index.html)
- [Environment variables used in Jina](https://docs.jina.ai/chapters/envs.html)
- ... [and more](https://docs.jina.ai/index.html)

## Community

- [Slack channel](https://join.slack.com/t/jina-ai/shared_invite/zt-dkl7x8p0-rVCv~3Fdc3~Dpwx7T7XG8w) - a communication platform for developers to discuss Jina
- [Community newsletter](mailto:newsletter+subscribe@jina.ai) - subscribe to the latest update, release and event news of Jina
- [LinkedIn](https://www.linkedin.com/company/jinaai/) - get to know Jina AI as a company and find job opportunities
- [![Twitter Follow](https://img.shields.io/twitter/follow/JinaAI_?label=Follow%20%40JinaAI_&style=social)](https://twitter.com/JinaAI_) - follow us and interact with us using hashtag `#JinaSearch`  
- [Company](https://jina.ai) - know more about our company, we are fully committed to open-source!



## License

Copyright (c) 2020 Jina AI Limited. All rights reserved.

Jina is licensed under the Apache License, Version 2.0. See [LICENSE](https://github.com/jina-ai/jina/blob/master/LICENSE) for the full license text.
