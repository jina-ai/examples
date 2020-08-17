__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import torch
from torch.autograd import Variable
# model is a file from the vsepp github
from model import VSE

from jina.executors.encoders.image.torchvision import ImageTorchEncoder


class VSEImageEncoder(ImageTorchEncoder):
    """
    :class:`VSEImageEncoder` encodes data from a ndarray, potentially B x (Channel x Height x Width) into a
        ndarray of `B x D`. using VSE img_emb branch

    """

    def __init__(self, path: str = 'runs/f30k_vse++_vggfull/model_best.pth.tar', *args, **kwargs):
        """
        :path : path where to find the model.pth file
        """
        super().__init__(*args, **kwargs)
        self.path = path

    def post_init(self):
        checkpoint = torch.load(self.path,
                                map_location=torch.device('cpu' if not self.on_gpu else 'cuda'))
        opt = checkpoint['opt']

        model = VSE(opt)
        model.load_state_dict(checkpoint['model'])
        model.img_enc.eval()
        self.model = model.img_enc
        del model.txt_enc

    def _get_features(self, data):
        # It needs Resize and Normalization before reaching this Point in another Pod
        # Check how this works, it may not be necessary to squeeze
        images = Variable(data, requires_grad=False)
        img_emb = self.model(images)
        return img_emb
