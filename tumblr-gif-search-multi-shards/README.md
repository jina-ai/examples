# tumblr-gif-search

This demo shows how to use Jina to build a video search engine.

## Prerequirements

This demo requires Python 3.7.

```bash
pip install -r requirements.txt
```

You also need to have Jina installed, please refer to [the installation guide](https://github.com/jina-ai/jina#getting-started), in particular following [the recommended way for developers](https://github.com/jina-ai/jina#dev-mode-install-from-your-local-folkclone).

## Download the data

```bash
python gif_download.py
```

There are quite some data, you may want to modify this code or [the file list](data/tgif-v1.0.tsv) to get only part of them.


## Run Index

```bash
python app.py
```

## Run Query

```bash
# change the Line 10 of app.py to 
# RUN_MODE = 'debug-query'
python app.py
```


## Troubleshootings

### `OSError: [Errno 24] Too many open files`

This often happens when `replicas`/`num_parallel` is set to a big number. Solution to that is to increase this (session-wise) allowance via:

```bash
ulimit -n 4096
```

### `objc[15934]: +[__NSPlaceholderDictionary initialize] may have been in progress in another thread when fork() was called.`

Probably MacOS only. 
```bash
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
```
