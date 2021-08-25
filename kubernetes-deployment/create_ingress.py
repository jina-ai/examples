from jina.peapods.pods.kubernetes.kubernetes_tools import ClientsSingelton
from kubernetes import config, client

def create_gateway_ingress(namespace: str):
    __clients_singelton = ClientsSingelton()
    # create ingress
    body = client.NetworkingV1beta1Ingress(
        api_version="networking.k8s.io/v1beta1",
        kind="Ingress",
        metadata=client.V1ObjectMeta(
            name=f'{namespace}-ingress',
            annotations={
                "nginx.ingress.kubernetes.io/rewrite-target": "/",
                # "linkerd.io/inject": "enabled",
            },
        ),
        spec=client.NetworkingV1beta1IngressSpec(
            rules=[
                client.NetworkingV1beta1IngressRule(
                    host="",
                    http=client.NetworkingV1beta1HTTPIngressRuleValue(
                        paths=[
                            client.NetworkingV1beta1HTTPIngressPath(
                                path="/",
                                backend=client.NetworkingV1beta1IngressBackend(
                                    service_port=8080, service_name="gateway-exposed"
                                ),
                            )
                        ]
                    ),
                )
            ]
        ),
    )
    # Creation of the Deployment in specified namespace
    # (Can replace "default" with a namespace you may have created)
    __clients_singelton.networking_v1_beta1_api.create_namespaced_ingress(namespace=namespace, body=body)
