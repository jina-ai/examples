# JINA 3分钟实现一套新闻搜索引擎

    经过上一篇介绍，我想大家已经jina有了一定的认识，如果还没有阅读的同学，在继续阅读之前，我们强烈建议先阅读上一篇[ JINA 100行代码搭建一套中文问答神经网络搜索引擎](https://github.com/jina-ai/examples/tree/webqa-search/webqa-search#jina-100%E8%A1%8C%E4%BB%A3%E7%A0%81%E6%90%AD%E5%BB%BA%E4%B8%80%E5%A5%97%E4%B8%AD%E6%96%87%E9%97%AE%E7%AD%94%E7%A5%9E%E7%BB%8F%E7%BD%91%E7%BB%9C%E6%90%9C%E7%B4%A2%E5%BC%95%E6%93%8E)。

    在上一篇中我们利用jina，实现了WebQA的搜索引擎的搭建，效果如大家所见，Awesome✌️✌️。

    我想大家在阅读完上一篇已经发现了，上一篇是基于短文本搜索短文本的，即问题搜索问题，创建索引和搜索时文档中的chunk只有一个，那么你或许会问jina能不能长文本搜索长文本呢，每个doc中有多个chunk？当然可以！

    那么，怎么做呢？请看如下分解。

## 导读

TODO



## 效果展示

TODO



## 总览

    在这个系统中我们采用数据集news-2016，数据集下载[地址](https://drive.google.com/file/d/1TMKu1FpTr6kcjWXWlQHX7YJsMfhhcVKp/view?usp=sharing)。数据集包含了250万篇新闻。新闻来源涵盖了6.3万个媒体，含标题、关键词、描述、正文。

    我们将新闻内容作为文档来创建索引；在搜索时，用户输入新闻内容，系统根据创建的索引利用`bi-match`算法召回topk相似的新闻。但是，无论是在创建索引的时候，还是在搜索的时候，系统都会根据分割子句的方式将新闻内容分割成多个子句，也就是分割成多个chunk。

## 环境依赖

    这个demo运行在Python3.7以上的环境。   

```shell
pip install -r requirements.txt
```



## 数据预处理

     在下载好数据集以后，我们将数据集放到`/tmp`文件夹中，运行下面命令。

```shell
python pre_data.py
```

## 搭建Flow

    与上一篇文章一样，我们通过YAML文件定义创建索引和搜索时的Flow。

    在创建索引时，我们定义了`extractor`，`doc_indexer`, `encoder`, `chunk_indexer`, `join`这5个Pod。

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

  extractor:
    yaml_path: extractor.yml
    needs: gateway

  encoder:
    image: jinaai/examples.hub.encoder.nlp.transformers-hit-scir
    timeout_ready: 60000

  chunk_indexer:
    yaml_path: chunk_indexer.yml

  join:
    yaml_path: merger
    needs: [doc_indexer, chunk_indexer]
```

</sub>

</td>
<td>
<img align="right" height="420px" src=".github/index.png"/>
</td>
</tr>
</table>

    在搜索时，我们定义了`extractor`, `encoder`, `chunk_indexer`,  `ranker`, `doc_indexer`这5个Pod。

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

  encoder:
    image: jinaai/examples.hub.encoder.nlp.transformers-hit-scir
    timeout_ready: 60000
    replicas: 2

  chunk_indexer:
    yaml_path: chunk_indexer.yml

  ranker:
    yaml_path: ranker.yml

  doc_indexer:
    yaml_path: doc_indexer.yml
```

</sub>

</td>
<td>
<img align="right" height="420px" src=".github/query.png"/>
</td>
</tr>
</table>

    在定义Flow的过程中，我们使用了jina中2个高级的功能，**容器化**和**弹性扩展**。不要听到高级功能就以为非常复杂，jina提供了非常简单的方式去使用这些高级功能。

### 容器化![whale](https://github.githubassets.com/images/icons/emoji/unicode/1f433.png)

    在上面你会发现，我们在定义`encoder`时，并没有加载YAML文件，而是加载了docker的镜像。

    在jina中Pod的加载可以从YAML文件中加载，可用从docker镜像中加载。同理，Flow的加载可以从YAML文件中加载，也可以从docker镜像中加载。

```yaml
!Flow
encoder:
    image: jinaai/examples.hub.encoder.nlp.transformers-hit-scir
    timeout_ready: 60000
```



### 弹性扩展![rocket](https://github.githubassets.com/images/icons/emoji/unicode/1f680.png)

    在定义`encoder`时，我们指定了`replicas`等于2，代表了在Pod中定义了2个Pea，并行编码chunk中的文本，这个参数在我们需要处理大批量数据时非常有用。

```yaml
!Flow
encoder:
    image: jinaai/examples.hub.encoder.nlp.transformers-hit-scir
    timeout_ready: 60000
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

    与第一篇文章一样，我们首先通过`build()`建立Flow，然后通过`index()`方法发送`bytes`数据和`IndexRequest`请求，在这里我们只发送新闻内容。

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

    for item in results:
        yield item

data_fn = os.path.join(workspace_path, "news2016zh_valid.json")
flow = Flow().load_config('flow-index.yml')
with flow.build() as fl:
    fl.index(raw_bytes=read_data(data_fn), batch_size=32)
```



### 查询

    在查询时，我们同样利用`build()`建立Flow，然后通过`search()`方法发送输入新闻内容的`bytes`，利用`print_topk()`输出相似新闻。

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
with flow.build() as fl:
    while True:
        content = input('请输入新闻内容: ')
        if not content:
            break
        item = {'content': content}

        ppr = lambda x: print_topk(x)
        fl.search(read_query_data(item), callback=ppr, topk=top_k)
```

    看了上面后，你会发现，无论是在查询时，还是在搜索时，这跟第一篇文章中Flow的Pod完全一致。确实一致，`doc_indexer`, `encoder`, `chunk_indxer`, `join`这4个Pod的处理逻辑和YAML文件的定义完全和第一篇文章中一模一样，但是`extractor`和`ranker`这两个Pod的处理逻辑跟第一篇文章中的处理逻辑却大大不同，那么有什么不同呢？继续往下走。

## 区别

### extractor

    在第一篇文章中，我们提到jina细化了文档的信息，引入了chunk的概念，将一个文档分割为多个chunk，每个chunk为基本的信息单元。

    我们根据新闻数据集存在的特点，开头信息对文本主旨贡献度较大，而越往后，则没那么重要。我们先将一篇新闻内容用`Sentencizer`进行子句分割，得到的一个chunk的列表，每个chunk中都是新闻内容的子句，然后采取了线性递减的方式给每个chunk赋予权重，开始的子句具有较高的权重，越往后的子句权重依次递减。这样做的好处是在搜索的过程中，让搜索关注权重较高的chunk。

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

    **重点来了，敲黑板**，在`chunk_indexer`后，文档中的每个chunk已经在创建的索引中查询到了topk的chunk。在WebQA中搜索时，每个文档下只有一个chunk；在这里，每个文档下有多个chunk。相当于WebQA是只对一个chunk下的topk chunk进行打分排序，而在这里是对所有chunk下的topk chunk进行打分排序。

    在`ranker`打分排序的过程中，`Chunk2DocScoreDriver`将文档下所有chunk id和topk chunk的文档，chunk_id，余弦距离组合在一起，提取chunk和topk chunk中ranker需要的值，在这里我们提取`weight`和`length`的值。并将这些值赋给`WeightBiMatchRanker`进行打分排序。

```python
from typing import Dict

import numpy as np
from jina.executors.rankers.bi_match import BiMatchRanker


class WeightBiMatchRanker(BiMatchRanker):
    required_keys = {'length', 'weight'}

    def score(self, match_idx: 'np.ndarray', query_chunk_meta: Dict, match_chunk_meta: Dict) -> 'np.ndarray':
        """ Apply weight into score, the weight contain query chunk weight, match chunk weight

        """
        for item, meta in zip(match_idx, match_chunk_meta):
            item[3] = item[3] * (1 / match_chunk_meta[meta]['weight'])

        for item, meta in zip(match_idx, query_chunk_meta):
            item[3] = item[3] * (1 / query_chunk_meta[meta]['weight'])

        return super().score(match_idx, query_chunk_meta, match_chunk_meta)

```

    在`WeightBiMatchRanker`中。我们利用刚刚提取的两个权重，进行余弦距离缩放。

> topk chunk的权重

    如果一个topk chunk的权重很小，说明我们在排序时应该尽可能的不关注它，让它的余弦距离应该足够大，在这里我们采用倒数机制来进行缩放，让topk chunk的余弦距离乘以topk chunk权重的倒数。

> chunk的权重

    如果一个chunk的权重很小，说明我们在排序时应该尽可能的不关注它的搜索结果，也就是让它的的topk下的chunk的余弦距离足够大，同样采用倒数机制，让topk chunk的余弦距离乘以chunk权重的倒数。

然后采用`bi-match`算法进行排序，得到是一个文档下所有topk chunk的排序打分，我们再利用topk chunk的文档id将topk chunk映射到topk文档，至此文档的topk相似文档就查询到了。



## 结语

    我们利用了Jina完成了2个搜索引擎的搭建，有没有感觉。Wow，好简单。所以，开始利用jina搭建自己的搜索引擎吧。

    详细项目[地址](https://github.com/jina-ai/examples/blob/webqa-search/news-search)，欢迎关注[jina](https://github.com/jina-ai/jina)。
