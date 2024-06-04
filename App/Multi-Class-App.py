# pip install gradio

import torch
import torchvision
import pandas as pd
import torch.nn as nn
import numpy as np
from PIL import Image
from torchvision import transforms, datasets
import gradio as gr
target_names = ['MEL','NV','BCC','AKIEC','BKL','DF','VASC']

unseen_transforms = transforms.Compose([
        transforms.Resize((224, 280)),
        transforms.CenterCrop((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

model1 = torchvision.models.resnet50(weights='ResNet50_Weights.IMAGENET1K_V1')#.to(device)

model1.fc = nn.Linear(2048, 7)#.to(device)

# load the last checkpoint with the best model
model1.load_state_dict(torch.load('skinmodel50.pt',map_location=torch.device('cpu'))) 

def prediction(input_img):
    image_pil = Image.fromarray(input_img).convert("RGB")
   
#     image = Image.open(image_pil).convert("RGB")
    image = unseen_transforms(image_pil)

    # Reshape the image to add batch dimension
    image = image.unsqueeze(0) 

    with torch.no_grad():
        model1.eval()
        inputs = image#.to(device)
        outputs = model1(inputs)
#         _, preds = torch.max(outputs, 1)
        pred1 = nn.functional.softmax(outputs, dim=1)#.cpu()
        _, pred = torch.max(pred1, 1)
        return target_names[pred[0].item()],f'Probability={torch.max(pred1):.3f}'   #target_names[preds[0].item()],outputs
    
demo = gr.Interface(prediction, gr.Image(), "text")
if __name__ == "__main__":
    demo.launch()