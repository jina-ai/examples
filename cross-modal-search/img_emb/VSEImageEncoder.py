__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import torch
from torch.autograd import Variable
from torchvision import transforms
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

        transformer = transforms.Compose([,
            transforms.Resize(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

        image = transformer(data)

        image = Variable(image, requires_grad=False)
        image = image.unsqueeze(0)
        if torch.cuda.is_available():
            image = image.cuda()
        img_emb = self.model(image)
        return img_emb
