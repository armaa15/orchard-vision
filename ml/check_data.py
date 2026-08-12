"""
check_data.py — verify PyTorch can read the DiaMOS pear leaf images.

"""

from collections import Counter
from pathlib import Path

from torch.utils.data import DataLoader
from torchvision import datasets, transforms

DATA_DIR = Path(__file__).parent / "data" / "Pear" / "leaves"

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

dataset = datasets.ImageFolder(root=DATA_DIR, transform=transform)

print(f"Looking in:   {DATA_DIR}")
print(f"Classes:      {dataset.classes}")
print(f"class_to_idx: {dataset.class_to_idx}")
print(f"Total images: {len(dataset)}")

print("\nPer-class counts:")
counts = Counter(dataset.targets)
for idx, name in enumerate(dataset.classes):
    n = counts[idx]
    print(f"  {name:<8} {n:>5}  ({n / len(dataset):.1%})")

loader = DataLoader(dataset, batch_size=32, shuffle=True)

images, labels = next(iter(loader))

print("\nOne batch:")
print(f"  Image tensor shape: {images.shape}")
print(f"  Label tensor shape: {labels.shape}")
print(f"  Labels in batch:    {labels.tolist()}")
print(f"  Pixel range:        {images.min():.3f} to {images.max():.3f}")