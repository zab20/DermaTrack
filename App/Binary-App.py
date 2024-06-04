import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models, datasets, transforms
from torch.utils.data import DataLoader, random_split
from torchvision import transforms
from PIL import Image

import gradio as gr
target = ['Benign','Malignant']
imgSize = 170


model = models.efficientnet_b7(weights = 'DEFAULT')
model.classifier[1] = nn.Linear(model.classifier[1].in_features, 1)
model.load_state_dict(torch.load('best_model.pth',map_location=torch.device('cpu'))) 

testTransformer = transforms.Compose([
                    transforms.Resize(size = (imgSize, imgSize), antialias = True),
                    transforms.CenterCrop(size = (imgSize, imgSize)),
                    transforms.ToTensor(),
                    transforms.Normalize(mean = [0.485, 0.456, 0.406], std = [0.229, 0.224, 0.225])])



def prediction(input_img):
    image_pil = Image.fromarray(input_img).convert("RGB")
    image = testTransformer(image_pil)
    image = image.unsqueeze(0) 

    with torch.no_grad():
        model.eval()
        inputs = image.to('cpu')
        outputs = model(inputs)
        predictions = (torch.sigmoid(outputs) > 0.5).float()
        predictions = int(predictions.item())
        prob = torch.sigmoid(outputs)[0][0].item()  
        prob = (1-prob if predictions==0 else prob)
        return target[predictions],f'Probability={prob:.3f}'
    
    
demo = gr.Interface(prediction, gr.Image(), "text")
if __name__ == "__main__":
    demo.launch()