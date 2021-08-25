import time

import numpy as np
import requests

from jina.peapods.pods.kubernetes import kubernetes_tools

kubernetes_tools.get_pod_logs("search-flow")

time.sleep(2)
input("Press Enter to start the requests...")

ip = '127.0.0.1'
port = '8080'
host = f'http://{ip}:{port}'

data = [{'embedding': np.ones((512,)).tolist()} for _ in range(1)]


def make_request(current):
    resp = requests.post(f'{host}/search', json={'data': data})
    print(f"Len response matches: {len(resp.json()['data']['docs'][0]['matches'])}")
    print(f'{current} resp', resp.status_code)


for i in range(10):
    print('request: ', i)
    make_request(i)
