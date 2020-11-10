__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os

from components import *
from helper import write_html, download_data, check_workdir, print_result
from jina.flow import Flow

# Set workdir and download urls
workdir = os.path.join("workdir")
query_data_url = "http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/t10k-images-idx3-ubyte.gz"
index_data_url = "http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/train-images-idx3-ubyte.gz"

# Check for working directory
check_workdir(workdir)

# Download data
targets = {
    "index": {
        "url": index_data_url,
        "filename": os.path.join(workdir, "index-original"),
    },
    "query": {
        "url": query_data_url,
        "filename": os.path.join(workdir, "query-original"),
    },
}
download_data(targets)

# Run index flow
f = Flow.load_config("flows/index.yml")
with f:
    f.index_ndarray(targets["index"]["data"], batch_size=1024)

# Run query flow
f = Flow.load_config("flows/query.yml")
with f:
    f.search_ndarray(
        targets["query"]["data"],
        shuffle=True,
        size=128,  # num_query
        output_fn=print_result,
        batch_size=32,
        top_k=50,
    )

# Write html
write_html(os.path.join(workdir, "hello-world.html"))
