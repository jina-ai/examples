import threading
import time

from jina.helper import colored
from jina.peapods.pods.kubernetes.kubernetes_tools import ClientsSingelton

__clients_singelton = ClientsSingelton()

def log_in_thread(pod_name, namespace, container):
    from kubernetes.watch import Watch

    pod = __clients_singelton.v1.read_namespaced_pod(pod_name, namespace)
    containers = [container.name for container in pod.spec.containers]
    if container not in containers:
        return
    w = Watch()
    for e in w.stream(
        __clients_singelton.v1.read_namespaced_pod_log,
        name=pod_name,
        namespace=namespace,
        container=container,
    ):
        print(colored(f"{pod_name}:{container} =>"), e)


def get_pod_logs(namespace):
    pods = __clients_singelton.v1.list_namespaced_pod(namespace)
    pod_names = [item.metadata.name for item in pods.items]
    for pod_name in pod_names:
        for container in [
            'executor',
            'istio-proxy',
            'dumper-init',
        ]:  # , 'linkerd-proxy']:
            x = threading.Thread(
                target=log_in_thread, args=(pod_name, namespace, container)
            )
            x.start()
            time.sleep(0.1)  # wait to get the logs after another
