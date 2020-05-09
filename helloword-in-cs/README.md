# Jina "Hello, World" in Client-Server Architecture

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

After playing with `jina hello-world` and reading its code, you may wonder if one can decouple the Flow and the send/receive part. It is particularly interesting in production, as one may run the Flow on one instance, whereas the request sending/receiving is from another.

![Hello-worl in CS](hello-world-cs.gif)

In this example, we will refactor the hello-world example into client-server architecture by using `py_client`.

## Flow as a Service

The complete server-side code can be found in [server.py](server.py). The key is to start the Flow and then hangs in there forever, dropping the request sending part. 

```python
import threading

# ...

f = Flow.load_config(args.index_yaml_path)
# run it!
with f:
    default_logger.success(f'hello-world server is started at {f.host}:{f.port_grpc}, '
                           f'you can now use "python client.py --port-grpc {f.port_grpc} --host {f.host}" to send request!')
    threading.Event().wait()
```

Here we use `threading.Event().wait()`, it is much more efficient way comparing to `while True: pass`.


You can start the server via:

```bash
python server.py
```

It will start the Flow and stop at

```text
Flow@50431[I]:6 Pods (i.e. 15 Peas) are running in this Flow
Flow@50431[S]:flow is now ready for use, current build_level is GRAPH
JINA@50431[S]:hello-world server is started at 0.0.0.0:58596, you can now use "python client.py --port-grpc 58596 --host 0.0.0.0" to send request!
```

`58596` is the port number we need to write down as it will be used on the client side. 

At any time, you can do `Ctrl+C` to terminate the server.

## Start the Client

The complete client-side code can be found in [client.py](client.py).

On the client side, we simply use `py_client` to connect to the server that we just launched. 

`host` and `port_grpc` are the most important arguments in the client.

```python
from jina.clients import py_client

# run it!
py_client(port_grpc=args.port_grpc, host=args.host).index(
    input_fn(targets['index']['filename']), batch_size=args.index_batch_size)
```

You can now start the client via:

```bash
python client --port-grpc 58596
```

In this example, our Flow and Client are on the same machine, so no host address is required. If you are running Flow remotely, please also add the remote IP address to `--host` and make sure the `port-grpc` is set to public in the remote security group.

It will show the progress bar on client side while indexing

```bash
PyClient@51641[S]:connected to the gateway at localhost:58596!
index [====================] 📃  20480 ⏱️ 11.4s 🐎 1796.8/s     20 batchx ...
index [====================] 📃  40960 ⏱️ 22.1s 🐎 1855.7/s     40 batch
index [=================== ] 📃  60416 ⏱️ 31.9s 🐎 1893.5/s     59 batch    [31.919 secs]
	✅ done in ⏱ 31.9s 🐎 1892.8/s
PyClient@51641[S]:terminated
```

And that's how you use Flow in a C/S manner. Pretty easy right?

## Take home message

- Use `with` context manager and `threading.Event().wait()` to start a Flow
- Use `py_client` to connect to a Flow with proper `host` and `port_grpc`
- Successful connection depends on the correct `host` and public accessible `port_grpc`

 

