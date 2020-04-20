# JINA 轻松实现一套新闻搜索引擎

## 前言

    经过上一篇介绍，我想大家已经jina有了一定的认识，如果还没有阅读的同学，可以点击[链接]()。

    在上一篇中我们利用jina，实现了WebQA的搜索引擎的搭建，效果如大家所见，还是**蛮不错的(*^__^*) 嘻嘻……。**我想大家在阅读完上一篇已经发现了，上一篇是基于短文本搜索短文本的，即title搜索title，搜索和索引中的doc中只有一个chunk，那么你或许会问jina能不能长文本搜索长文本呢，每个doc中有多个chunk？当然可以！

    那么，怎么做呢？请看如下分解。

## 效果展示

### Index Flow

    还是跟前篇文章一样，我们先来看创建索引和搜索时Flow的代码。

    在Flow的定义中各个Pod的功能和WebQA中定义的Flow没有什么区别。区别的地方在于extractor和ranker中Pod的详细逻辑。

```python
index_flow = (Flow().add(name='extractor', yaml_path='extractor.yml')
 .add(name='md_indexer', yaml_path='md_indexer.yml',needs='gateway')
 .add(name='encoder', yaml_path='encoder.yml', needs='extractor', timeout_ready=600000)
 .add(name='cc_indexer',yaml_path='cc_indexer.yml', needs='encoder')
 .join(['cc_indexer', 'md_indexer']))
```

### Query Flow

```python
query_flow = (Flow().add(name='extractor', yaml_path='extractor.yml')
 .add(name='encoder', yaml_path='encoder.yml', needs='extractor', timeout_ready=60000)
 .add(name='cc_indexer', yaml_path='cc_indexer.yml', needs='encoder', timeout_ready=60000)
 .add(name='ranker', yaml_path='ranker.yml', needs='cc_indexer')
 .add(name='md_indexer', yaml_path='md_indexer.yml', needs='ranker'))
```

## 数据集

    在这个系统中，我们采用的数据集为中文新闻2016版。采用新闻正文内容来建立索引。

### 数据描述

    包含了250万篇新闻。新闻来源涵盖了6.3万个媒体，含标题、关键词、描述、正文。

数据集划分：数据去重并分成三个部分。训练集：243万；验证集：7.7万；测试集，数万。下载[链接](https://drive.google.com/file/d/1TMKu1FpTr6kcjWXWlQHX7YJsMfhhcVKp/view?usp=sharing)。

### 结构

```json
{'news_id': <news_id>,'title':<title>,'content':<content>,'source': <source>,'time':<time>,'keywords': <keywords>,'desc': <desc>, 'desc': <desc>}

其中，title是新闻标题，content是正文，keywords是关键词，desc是描述，source是新闻的来源，time是发布时间
```

### 例子

```json
{"news_id": "610130831", "keywords": "导游，门票","title": "故宫淡季门票40元 “黑导游”卖外地客140元", "desc": "近日有网友微博爆料称，故宫午门广场售票处出现“黑导游”，专门向外地游客出售高价门票。昨日，记者实地探访故宫，发现“黑导游”确实存在。窗口出售", "source": "新华网", "time": "03-22 12:00", "content": "近日有网友微博爆料称，故宫午门广场售票处出现“黑导游”，专门向外地游客出售高价门票。昨日，记者实地探访故宫，发现“黑导游”确实存在。窗口出售40元的门票，被“黑导游”加价出售，最高加到140元。故宫方面表示，请游客务必通过正规渠道购买门票，避免上当受骗遭受损失。目前单笔门票购买流程不过几秒钟，耐心排队购票也不会等待太长时间。....再反弹”的态势，打击黑导游需要游客配合，通过正规渠道购买门票。"}
```

## 搭建过程

### 创建索引

    在创建索引时，与WebQA有区别的地方在于extractor这个Pod，所以我们只对extractor进行详细的介绍，其他模块不做介绍，如果对其它模块有疑问的地方，可以参考第一篇[文章]()。

![](/Users/maxiong/workpace/jina/examples/news-search/pictures/index.jpg)

#### extractor

    在第一篇文章中，我们提到jina细化了doc中的信息，引入了chunk的概念，将一个doc分割为多个chunk，每个chunk为基本的信息单元，搜索的时候以chunk为基本单位进行搜索，然后将chunk的搜索结果映射回doc进行召回。这样做的好处是因为doc携带的信息过多，在搜索的时候容易存在信息干扰，所以分割doc以后，搜索在最基本的信息单元进行，有利于提升搜索精准度。

    根据新闻数据集存在的特点，开头信息对文本主旨贡献度较大，而越往后，则没那么重要。所以我们先将一篇新闻内容以“。！？”等句子分隔符进行分割，得到的一个chunk的list，然后采取了线性递减的方式给每个chunk赋予权重，开始的子句具有较高的权重，越往后的子句权重依次递减。这样做的好处是在搜索的过程中，让搜索关注权重较高的chunk。

```python
class WeightSentencizer(Sentencizer):
    def craft(self, raw_bytes: bytes, doc_id: int, *args, ** kwargs) -> List[Dict]:
        results = super().craft(raw_bytes, doc_id)
        weights = np.linspace(1, 0.1, len(results))
        for result, weight in zip(results, weights):
            result['weight'] = weight

        return results
```



### 查询

    在查询时，Flow的结构与WebQA一样，有区别的Pod是extractor、ranker。下面我们对这两个pod进行详细的介绍，其它Pod不做介绍，如果对其它模块有疑问的地方，可以参考第一篇[文章]()。

![](/Users/maxiong/workpace/jina/examples/news-search/pictures/query.jpg)

#### extractor

    当查询的时候，输入的是一个新闻文本，我们跟创建索引时一样，将新闻文本分割多个chunk，并赋予线性递减的权重，开始的子句具有较高的权重，越往后的子句具有较低的权重。

#### ranker

    在cc_indexer后，每个chunk已经在索引中查询到了topk的chunk，

    在每个`chunk`找出对应的`top_k`以后，我们需要对每个`doc`下的所有`chunk`的`top_k``chunk`进行排序，融合成`doc`下的`top_k chunk`，因为我们刚刚找出的是每个`chunk`下的`top_k`，所有的`chunk`下的`top_k`需要进行排序。

```yaml
!BiMatchRanker
metas:
  name: ranker
  py_modules: weight.py
requests:
  on:
    SearchRequest:
      - !ChunkWeightDriver
        with:
          reverse: true
      - !Chunk2DocScoreDriver
        with:
          method: score
      - !DocPruneDriver {}
```

## 结语

    我们利用了Jina完成了2个搜索引擎的搭建，有没有感觉。Wow，好简单。所以，开始利用Jina搭建自己的搜索引擎吧。

    详细项目[地址](https://github.com/jina-ai/examples/blob/webqa-search/news-search)，欢迎关注[jina](https://github.com/jina-ai/jina)。
