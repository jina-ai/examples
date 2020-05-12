# JINA 3分钟实现一套新闻搜索系统

    经过上一篇介绍，我想大家已经jina有了一定的认识，如果还没有阅读的同学，在继续阅读之前，我们强烈建议先阅读上一篇[ JINA 100行代码搭建一套中文问答神经网络搜索引擎](https://github.com/jina-ai/examples/tree/webqa-search/webqa-search#jina-100%E8%A1%8C%E4%BB%A3%E7%A0%81%E6%90%AD%E5%BB%BA%E4%B8%80%E5%A5%97%E4%B8%AD%E6%96%87%E9%97%AE%E7%AD%94%E7%A5%9E%E7%BB%8F%E7%BD%91%E7%BB%9C%E6%90%9C%E7%B4%A2%E5%BC%95%E6%93%8E)。

    在上一篇中我们利用jina，实现了WebQA的搜索引擎的搭建，效果如大家所见，Awesome✌️✌️。

    我想大家在阅读完上一篇已经发现了，上一篇是我们是使用问题搜索问题，基于短文本搜索短文本，所以在创建索引和查询时Document中的Chunk都只有一个。那么你或许会问jina能不能长文本搜索长文本呢？当然可以！在这个教程中我们将通过让每个Document中包含多个Chunk来实现长文本搜索。

    那么，怎么做呢？请看如下分解。

## 导读

- [效果展示](#效果展示)
- [总览](#总览)
- [环境依赖](#环境依赖)
- [数据预处理](#数据预处理)
- [搭建Flow](#搭建Flow)
- [运行Flow](#运行Flow)
- [使用多个Chunk和深入ranker](#使用多个Chunk和深入ranker)
- [回顾](#回顾)
- [结语](#结语)

## 效果展示

![效果展示](.github/result.gif)

## 总览

    在这篇文章中我们主要介绍如何使用jina实现一个长文本的新闻内容搜索系统，阅读完本篇以后，你将会学到：

1. Document存在多个Chunk时，jina如何进行查询？

2. 如何使用jina进行弹性扩展？

3. 如何使用jina加载docker镜像，摆脱复杂环境依赖？

4. 在查询时，ranker的作用是什么？

## 环境依赖

    这个demo运行在Python3.7以上的环境。   

```shell
pip install -r requirements.txt
```

## 数据预处理

        在这个系统中我们采用数据集news-2016，数据集下载[百度云](https://pan.baidu.com/share/init?surl=MLLM-CdM6BhJkj8D0u3atA)，密码：k265。数据集包含了250万篇新闻。新闻来源涵盖了6.3万个媒体，含标题、关键词、描述、正文。

     在下载好数据集以后，我们将数据集放到`/tmp`文件夹中，运行下面命令。

```shell
python prepare_data.py
```

## 搭建Flow

    与上一篇文章一样，我们通过YAML文件定义创建索引和查询任务的Flow。

    在创建索引时，我们定义了`extractor`，`doc_indexer`, `encoder`, `chunk_indexer`, `join`5个Pod。

<table style="margin-left:auto;margin-right:auto;">
<tr>
<td> flow-index.yml</td>
<td> Flow in Dashboard</td>
</tr>
<tr>
<td>
  <sub>

```yaml
!Flow
pods:
  doc_indexer:
    yaml_path: doc_indexer.yml
    replicas: 2

  extractor:
    yaml_path: extractor.yml
    needs: gateway
    replicas: 2

  encoder:
    image: jinaai/examples.hub.encoder.nlp.transformers-hit-scir
    timeout_ready: 60000
    replicas: 2

  chunk_indexer:
    yaml_path: chunk_indexer.yml
    replicas: 2

  join:
    yaml_path: _merger
    needs: [doc_indexer, chunk_indexer]
```

</sub>

</td>
<td>
<img align="right" height="420px" src=".github/index.png"/>
</td>
</tr>
</table>

    在查询任务中，我们定义了`extractor`, `encoder`, `chunk_indexer`,  `ranker`, `doc_indexer`5个Pod。

<table style="margin-left:auto;margin-right:auto;">
<tr>
<td> flow-query.yml</td>
<td> Flow in Dashboard</td>
</tr>
<tr>
<td>
  <sub>

```yaml
!Flow
pods:
  extractor:
    yaml_path: extractor.yml
    replicas: 2

  encoder:
    image: jinaai/examples.hub.encoder.nlp.transformers-hit-scir
    timeout_ready: 6000000
    replicas: 2

  chunk_indexer:
    yaml_path: chunk_indexer.yml
    replicas: 2

  ranker:
    yaml_path: ranker.yml
    replicas: 2

  doc_indexer:
    yaml_path: doc_indexer.yml
    replicas: 2
```

</sub>

</td>
<td>
<img align="right" height="420px" src=".github/query.png"/>
</td>
</tr>
</table>

    在定义Flow的过程中，我们使用了jina中2个高级的功能，**容器化**和**弹性扩展**。不要听到高级功能就以为非常复杂哦，jina提供了非常简单的方式去使用这些高级功能。

### 容器化🐳

    jina加载一个Pod时，提供了2种简单的方式：

1. 通过YAML文件，我们在上一个例子中已经反复使用。

2. 通过docker镜像。

    例如，我们在定义`encoder`时，并没有加载YAML文件，而是通过`image`指定了Roberta的docker的镜像。为什么要这样做呢？因为使用docker镜像可以摆脱复杂的环境依赖，达到即插即用的效果。

```yaml
!Flow
encoder:
    image: jinaai/examples.hub.encoder.nlp.transformers-hit-scir
```

### 弹性扩展🚀

    在定义Pod时，我们设置了Pod的`replicas`参数，代表了在Pod中定义了多个Pea，并行处理请求。例如在定义`encoder` Pod时，我们设置了`replicas`为2，代表了有2个Pea并行编码Chunk中的文本。

    如果我们需要处理大批量数据时，这个参数将非常有用。

```yaml
!Flow
encoder:
    image: jinaai/examples.hub.encoder.nlp.transformers-hit-scir
    replicas: 2
```

## 运行Flow

### 创建索引

```python
python app.py -t index
```

<details>
<summary>点击查看日志输出</summary>

<p align="center">
  <img src=".github/index-log.gif?raw=true" alt="日志输出">
</p>

</details>

    与第一篇文章创建索引时一样，我们通过`flow-index.yml`定义创建索引任务的Flow，然后通过`index()`函数对数据进行创建索引。在这里我们只发送新闻内容。为了节省运行时间，我们只创建10000条索引。

```python
def read_data(fn):
    items = []
    with open(fn, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.replace('\n', '')
            item = json.loads(line)
            content = item['content']
            if content == '':
                continue
            items.append({'content': content})
    results = []
    for content in items:
        results.append(("{}".format(json.dumps(content, ensure_ascii=False))).encode("utf-8"))

    for item in results[:10000]:
        yield item

data_fn = os.path.join(workspace_path, "news2016zh_train.json")
flow = Flow().load_config('flow-index.yml')
with flow:
    flow.index(read_data(data_fn))
```

### 查询

```python
python app.py -t query
```

<details>
<summary>点击查看日志输出</summary>

<p align="center">
  <img src=".github/query-log.gif?raw=true" alt="日志输出">
</p>

</details>

    在查询时，我们同样通过`flow-query.yml`定义查询任务的Flow。 然后通过`search()`方法发送希望查询的新闻内容，利用`print_topk()`输出相似新闻。

```python
def print_topk(resp):
    print(f'以下是相似的新闻内容:')
    for d in resp.search.docs:
        for tk in d.topk_results:
            item = json.loads(tk.match_doc.raw_bytes.decode('utf-8'))
            print('→%s' % item['title'])

def read_query_data(item):
    yield ("{}".format(json.dumps(item, ensure_ascii=False))).encode('utf-8')

flow = Flow().load_config('flow-query.yml')
with flow:
    while True:
        content = input('请输入新闻内容: ')
        if not content:
            break
        item = {'content': content}

        ppr = lambda x: print_topk(x)
        flow.search(read_query_data(item), callback=ppr, topk=top_k)
```

    看了上面后，你会发现，无论是在创建索引任务中，还是在查询任务中，这跟第一篇文章中Flow的Pod完全一致。确实一致，`doc_indexer`, `encoder`, `chunk_indxer`, `join`这4个Pod的处理逻辑和YAML文件的定义完全和第一篇文章中一模一样，但是`extractor`和`ranker`这两个Pod的处理逻辑跟第一篇文章中的处理逻辑却大大不同，那么有什么不同呢？继续往下走。

## 使用多个Chunk和深入ranker

### extractor

    在第一篇文章中，我们提到jina细化了Document的信息，引入了Chunk的概念。将一个Document转换为多个Chunk，每个Chunk为基本的信息单元。

    我们先将一篇新闻内容用`Sentencizer`进行子句分割，得到的一个Chunk的列表，每个Chunk中都是新闻内容的子句。在jina中，每个Chunk在索引时都可以被赋予一个在该Document中的权重。在这里，我们根据新闻数据集存在的特点，设定线性递减的方式给每个Chunk赋予权重。换句话说，开始的子句具有较高的权重，越往后的子句权重依次递减。

```python
class WeightSentencizer(Sentencizer):
    def craft(self, raw_bytes: bytes, doc_id: int, *args, ** kwargs) -> List[Dict]:
        results = super().craft(raw_bytes, doc_id)
        weights = np.linspace(1, 0.1, len(results))
        for result, weight in zip(results, weights):
            result['weight'] = weight
    
        return results
```

### ranker

    **重点来了，敲黑板**， 在查询时刻，`extractor`将需要查询的Document拆分为多个查询Chunk。在`chunk_indexer`后，其中的每个查询Chunk都已经从索引中找到了相似的Chunk，也就是召回Chunk。 现在轮到`ranker`登场了，`ranker`的作用是根据这些找到的相似Chunk来找到与查询Document相似的Document。

    `ranker`的处理过程是:

1. `ranker`中的`Chunk2DocScoreDriver`将`WeightBiMatchRanker`所需要的数据准备好。

2. `ranker`调用`WeightBiMatchRanker`的`score()`方法根据相似Chunk中的信息计算相似Document的分数。

3. `ranker`将相似Document的信息和分数写入Flow的数据流中。  

    在这里我们继承`BiMatchRanker`实现了`WeightBiMatchRanker`作为`ranker`的Executor。在`WeightBiMatchRanker`中，我们复写了`score()`。在`socre()`方法中，我们先使用了查询Chunk和召回Chunk的`weight`对召回Chunk的分数进行了调整；然后使用了`bi-match`算法计算相似Document的分数。这里我们的分数计算只是一个简单的例子，抛砖引玉，大家不必纠结与这里分数计算的细节。更重要的是希望大家能掌握如何定义自己的`ranker`。

```python
from typing import Dict

from jina.executors.rankers.bi_match import BiMatchRanker


class WeightBiMatchRanker(BiMatchRanker):
    required_keys = {'length', 'weight'}

    def score(self, match_idx: 'np.ndarray', query_chunk_meta: Dict, match_chunk_meta: Dict) -> 'np.ndarray':
        """ Apply weight into score, the weight contain query chunk weight, match chunk weight
        :param match_idx: a [N x 4] numpy ``ndarray``, column-wise:

                - ``match_idx[:, 0]``: ``doc_id`` of the matched chunks, integer
                - ``match_idx[:, 1]``: ``chunk_id`` of the matched chunks, integer
                - ``match_idx[:, 2]``: ``chunk_id`` of the query chunks, integer
                - ``match_idx[:, 3]``: distance/metric/score between the query and matched chunks, float
        :param query_chunk_meta: the meta information of the query chunks, where the key is query chunks' ``chunk_id``,
            the value is extracted by the ``required_keys``.
        :param match_chunk_meta: the meta information of the matched chunks, where the key is matched chunks'
            ``chunk_id``, the value is extracted by the ``required_keys``.

        """
        for item, meta in zip(match_idx, match_chunk_meta):
            item[3] = item[3] * (1 / match_chunk_meta[meta]['weight'])

        for item, meta in zip(match_idx, query_chunk_meta):
            item[3] = item[3] * (1 / query_chunk_meta[meta]['weight'])

        return super().score(match_idx, query_chunk_meta, match_chunk_meta)
```

## 回顾

1. jina中Document可以包含多个Chunk。Chunk是jina建立索引和查询的最基本处理单元。

2. jina支持容器化，只需要在定义Pod时将`yaml_path`字段更改为`image`，并添加相应镜像的名称。

3. jina支持弹性扩展，只需要在Pod中增加`replicas`字段。

4. 在查询任务中，`ranker`的作用是根据找到的召回的Chunk得到与查询Document相似的Document。

## 文档

    要深入学习Jina，最好的方法就是阅读我们的文档。文档建立在主分支的每个推送、合并和发布事件上。你可以在我们的文档中找到关于以下主题的更多细节。

- [Jina命令行接口参数解释](https://docs.jina.ai/chapters/cli/main.html)
- [Jina Python API接口](https://docs.jina.ai/api/jina.html)
- [用于执行器、驱动和流程的Jina YAML语法](https://docs.jina.ai/chapters/yaml/yaml.html)
- [Jina Protobuf方案](https://docs.jina.ai/chapters/proto/main.html)
- [Jina中使用的环境变量](https://docs.jina.ai/chapters/envs.html)
- ..[以及更多](https://docs.jina.ai/index.html)

## 社区
- [Slack频道](https://join.slack.com/t/jina-ai/shared_invite/zt-dkl7x8p0-rVCv~3Fdc3~Dpwx7T7XG8w) - 为开发者提供交流平台，探讨Jina
- [社区通讯](mailto:newsletter+subscribe@jina.ai) - 订阅Jina的最新更新、发布和活动消息，订阅Jina的最新动态、发布和活动消息。
- [LinkedIn](https://www.linkedin.com/company/jinaai/) - 了解Jina AI公司并寻找工作机会
- ![Twitter Follow](https://img.shields.io/twitter/follow/JinaAI_?label=Follow%20%40JinaAI_&style=social) - 关注我们，并使用tag标签与我们互动`#JinaSearch`  
- [公司](https://jina.ai/) - 了解更多关于我们公司的信息，我们完全致力于开源!

## 许可证

Copyright (c) 2020 Jina AI Limited.保留所有权利。

Jina是在Apache License 2.0版本下授权的。[许可证全文见LICENSE。](https://github.com/jina-ai/jina/blob/master/LICENSE)
