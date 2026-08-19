"""
model.py — ResNet18 with a replaced final layer, for four-class leaf disease.
"""

import torch
import torch.nn as nn
from torchvision import models


def build_model(num_classes=4, freeze_backbone=True):
    """Return a ResNet18 pretrained on ImageNet with a new final layer."""
    weights = models.ResNet18_Weights.IMAGENET1K_V1
    model = models.resnet18(weights=weights)

    if freeze_backbone:
        for param in model.parameters():
            param.requires_grad = False

    # model.fc is the final layer. in_features is however many features the
    # backbone produces (512 for ResNet18); read it rather than hardcode it.
    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, num_classes)

    return model


def get_device():
    """Return the GPU if one is reachable, otherwise the CPU."""
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


if __name__ == "__main__":
    device = get_device()
    print(f"Device: {device}")
    if device.type == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}")

    model = build_model()
    model = model.to(device)

    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"\nTotal parameters:     {total:,}")
    print(f"Trainable parameters: {trainable:,}  ({trainable / total:.2%})")
    print(f"Final layer: {model.fc}")

    # Forward pass on fake data — shape check only, no real images needed.
    dummy = torch.randn(4, 3, 224, 224).to(device)
    with torch.no_grad():
        output = model(dummy)
    print(f"\nInput shape:  {tuple(dummy.shape)}")
    print(f"Output shape: {tuple(output.shape)}")
    print(f"Raw outputs for first image: {output[0].tolist()}")