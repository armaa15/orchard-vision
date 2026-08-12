"""
data.py — dataset construction and a stratified train/validation split.

"""

from collections import Counter
from pathlib import Path

from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, transforms

DATA_DIR = Path(__file__).parent / "data" / "Pear" / "leaves"

# Statistics of the ImageNet training set, per RGB channel.
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
])

# Kept separate from train_transform on purpose: augmentation gets added
# to the training pipeline later and must never touch validation.
val_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
])


def build_datasets(val_fraction=0.2, seed=42):
    """Return (train_subset, val_subset, class_names)."""
    train_base = datasets.ImageFolder(root=DATA_DIR, transform=train_transform)
    val_base = datasets.ImageFolder(root=DATA_DIR, transform=val_transform)

    indices = list(range(len(train_base)))

    train_idx, val_idx = train_test_split(
        indices,
        test_size=val_fraction,
        stratify=train_base.targets,
        random_state=seed,
    )

    return (
        Subset(train_base, train_idx),
        Subset(val_base, val_idx),
        train_base.classes,
    )


def build_dataloaders(batch_size=32, val_fraction=0.2, seed=42):
    """Return (train_loader, val_loader, class_names)."""
    train_ds, val_ds, classes = build_datasets(val_fraction, seed)

    train_loader = DataLoader(
        train_ds, batch_size=batch_size, shuffle=True,
        num_workers=4, pin_memory=True,
    )
    val_loader = DataLoader(
        val_ds, batch_size=batch_size, shuffle=False,
        num_workers=4, pin_memory=True,
    )
    return train_loader, val_loader, classes


def _summarise(subset, classes, name):
    labels = [subset.dataset.targets[i] for i in subset.indices]
    counts = Counter(labels)
    print(f"\n{name} — {len(subset)} images")
    for idx, class_name in enumerate(classes):
        n = counts[idx]
        print(f"  {class_name:<8} {n:>5}  ({n / len(subset):.1%})")


if __name__ == "__main__":
    train_ds, val_ds, classes = build_datasets()
    print(f"Classes: {classes}")
    _summarise(train_ds, classes, "TRAIN")
    _summarise(val_ds, classes, "VALIDATION")

    train_loader, val_loader, _ = build_dataloaders()
    images, labels = next(iter(train_loader))
    print(f"\nOne training batch: {images.shape}")
    print(f"  Pixel range after normalisation: "
          f"{images.min():.3f} to {images.max():.3f}")