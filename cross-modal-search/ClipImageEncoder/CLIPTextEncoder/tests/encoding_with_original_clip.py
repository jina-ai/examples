import numpy as np
import clip
import torch
import torch.utils.data as data
import PIL
from PIL import Image

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load('ViT-B/32', device)

### Encoding a single item

text = 'Han likes eating pizza'
embeddeding_tensor = model.encode_text(clip.tokenize(text))
embedding_np = embeddeding_tensor.detach().numpy()

file = open('./expected.npy','bw')
np.save(file, embedding_np)
file.close()

### Encoding a batch

text = np.array(['Han likes eating pizza', 'Han likes pizza', 'Jina rocks'])
device='cpu'
embedding_batch_tensor =  model.encode_text(clip.tokenize(text))
embedding_batch_np = embedding_batch_tensor.detach().numpy()
file = open('./expected_batch.npy','bw')
np.save(file, embedding_batch_np)
file.close()

