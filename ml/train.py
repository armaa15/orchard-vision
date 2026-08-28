"""
train.py — fine-tune the final layer of ResNet18 on DiaMOS pear leaves.

Baseline run: no imbalance handling. This establishes the naive result
that later versions are measured against.

Run from inside ml/ with the venv active:  python train.py
"""

import time
from pathlib import Path

import torch
import torch.nn as nn

from data import build_dataloaders
from model import build_model, get_device
from collections import Counter

CHECKPOINT_DIR = Path(__file__).parent / "checkpoints"
EPOCHS = 10
LEARNING_RATE = 1e-3


def run_epoch(model, loader, criterion, device, optimizer=None):
    """One full pass over loader. Trains if an optimizer is given, else evaluates."""
    is_train = optimizer is not None

    if is_train:
        model.train()
    else:
        model.eval()

    total_loss = 0.0
    correct = 0
    seen = 0

    with torch.set_grad_enabled(is_train):
        for images, labels in loader:
            images = images.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)

            outputs = model(images)
            loss = criterion(outputs, labels)

            if is_train:
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            # loss is already averaged over the batch, so multiply back up
            # before summing — the last batch is smaller than the rest.
            total_loss += loss.item() * labels.size(0)
            correct += (outputs.argmax(dim=1) == labels).sum().item()
            seen += labels.size(0)

    return total_loss / seen, correct / seen

def compute_class_weights(train_subset, num_classes, device):
    count = len(train_subset)
    indices = train_subset.indices
    labels = [train_subset.dataset.targets[c] for c in indices]
    counts = Counter(labels)
    weights = [
        count / (num_classes * counts[c]) if counts[c] > 0.0 else 0.0
        for c in range(num_classes)
    ]
    return torch.tensor(weights, dtype=torch.float32, device=device)

def main():
    device = get_device()
    print(f"Device: {device}")

    train_loader, val_loader, classes = build_dataloaders()
    print(f"Classes: {classes}")
    print(f"Train batches: {len(train_loader)}   Val batches: {len(val_loader)}")

    model = build_model(num_classes=len(classes)).to(device)

    weights = compute_class_weights(train_loader.dataset, len(classes), device)
    criterion = nn.CrossEntropyLoss(weight=weights)
    optimizer = torch.optim.Adam(
        [p for p in model.parameters() if p.requires_grad],
        lr=LEARNING_RATE,
    )

    CHECKPOINT_DIR.mkdir(exist_ok=True)
    best_val_acc = 0.0

    for epoch in range(1, EPOCHS + 1):
        start = time.time()

        train_loss, train_acc = run_epoch(
            model, train_loader, criterion, device, optimizer
        )
        val_loss, val_acc = run_epoch(model, val_loader, criterion, device)

        elapsed = time.time() - start

        print(
            f"Epoch {epoch:>2}/{EPOCHS}  "
            f"train loss {train_loss:.4f} acc {train_acc:.3f}  |  "
            f"val loss {val_loss:.4f} acc {val_acc:.3f}   ({elapsed:.1f}s)"
        )

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(
                {
                    "model_state": model.state_dict(),
                    "classes": classes,
                    "epoch": epoch,
                    "val_acc": val_acc,
                },
                CHECKPOINT_DIR / "weighted_cached-fix_best.pth",
            )
            print(f"          ↳ saved new best ({val_acc:.3f})")

    print(f"\nBest validation accuracy: {best_val_acc:.3f}")


if __name__ == "__main__":
    main()