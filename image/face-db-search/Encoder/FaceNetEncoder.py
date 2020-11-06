__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"


from jina.executors.encoders.frameworks import BaseCVTorchEncoder

class FaceNetTorchEncoder(BaseCVTorchEncoder):
    """
    :class:`FaceNetTorchEncoder` encodes data from a ndarray, potentially B x (Channel x Height x Width) into a
        ndarray of `B x D`.

    """

    def __init__(self,pretrained: str='vggface2', *args, **kwargs):
        """
        :pretrained : The weights to load
        """
        super().__init__(*args, **kwargs)
        if pretrained not in ('vggface2','casia-webface'):
            raise NotImplementedError('unknown pretrained checkpoints: {}'.format(self.pretrained))
        self.pretrained = pretrained

    def post_init(self):
        from facenet_pytorch import InceptionResnetV1
        self.model= InceptionResnetV1(pretrained=self.pretrained).eval()
        self.to_device(self.model)

    def _get_features(self, data):
        return self.model(data)
