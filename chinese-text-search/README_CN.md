# 基于Transformer的中文文字搜索

| 列表        | 内容           |
| ------------- |:-------------:|
| 输入     | 一个text文本文件 |
| 输出     | top_k 个匹配查询的句子| 
| Jina版本 | 1.0.0   |
 
这是一个使用[Jina](http://www.jina.ai) 神经搜索框架来对红楼梦第一章节进行搜索的例子。这个例子使用了基于 [Transformers](https://huggingface.co) 的[`bert-base-chinese`](https://huggingface.co/bert-base-chinese) 预训练模型。

## 安装

```sh
pip install -r requirements.txt
```

## 开始

我们先从一个小的数据集(`data/toy-data.txt`) 开始进行建立索引与搜索，以确保其功能性的正确。执行以下两个命令即可在终端进行交互式搜索。

```sh
python app.py -t index
```

```sh
python app.py -t query
```

## 建立索引

如果想索引更大的数据集 [full dataset](https://www.kaggle.com/noxmoon/chinese-official-daily-news-since-2016):

1. 配置 [Kaggle](https://www.kaggle.com/docs/api#getting-started-installation-&-authentication)
2. 执行: `sh ./get_data.sh`
3. 配置输入文件: `export JINA_DATA_FILE='data/chinese_news.txt'`
4. 配置索引数据数量 `export JINA_MAX_DOCS=500` (or whatever number you prefer. The default is `50`)
5. 删除旧的工作空间（存储索引数据）: `rm -rf workspace`
6. 为新的数据集建立索引: `python app.py -t index`

## 进行搜索

### 使用 REST API

```sh
python app.py -t query_restful
```

接着可以进行`curl`发出搜索请求:

```sh
curl --request POST -d '{"top_k": 10, "mode": "search",  "data": ["text: 满纸荒唐言，一把辛酸泪"]}' -H 'Content-Type: application/json' 'http://0.0.0.0:45678/api/search'
````

或者使用 [Jinabox](https://jina.ai/jinabox.js/) 用 `http://127.0.0.1:45678/api/search` 进行搜索。

### 使用终端

```sh
python app.py -t query
```

## 建立 Docker 镜像

我们还可以按照如下方式建立包含预先索引好的数据和端口的Docker镜像，进而进行REST查询。

1. 执行`配置环境`和`建立索引`, 不要执行搜索步骤；
2. 如果你想 [上传镜像到Jina Hub](#上传到Jina Hub)，请确保编辑好`Dockerfile`中的`LABEL`避免和其他镜像冲突；
3. 根目录中执行 `docker build -t <your_image_name> .`；
5. 执行 `docker run -p 45678:45678 <your_image_name>`；
6. 进行搜索。

### 镜像命名规范

请遵循如下规范对Docker镜像进行命名，否则无法上传Jina hub。

```
jinahub/type.kind.image-name:image-version-jina_version
```

比如:

```
jinahub/app.example.chiese-text-search:0.0.1-1.0.0
```

## 上传到 [Jina Hub](https://github.com/jina-ai/jina-hub)

1. 确保安装 `pip install jina[hub]==1.0.0`
2. 执行 `jina hub login` 并把相应代码粘贴到浏览器中鉴权
3. 执行 `jina hub push <your_image_name>`
