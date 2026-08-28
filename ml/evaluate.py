"""
evaluate.py — per-class metrics and a confusion matrix for a saved checkpoint.

Accuracy is one number averaged over four very unequal classes. This is the
script that says what the model actually does with the rare ones.

Run from inside ml/ with the venv active:  python evaluate.py
"""

from pathlib import Path

import torch
from sklearn.metrics import classification_report, confusion_matrix

from data import build_dataloaders
from model import build_model, get_device

import argparse

CHECKPOINT = Path(__file__).parent / "checkpoints" / "weighted_cached-fix_best.pth"


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run",
        default="unnamed",
        help="Run name. Reads checkpoints/{run}_best.pth",
    )
    return parser.parse_args()


def collect_predictions(model, loader, device):
    """Run the model over loader and return (true_labels, predicted_labels)."""
    model.eval()
    all_true = []
    all_pred = []

    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device, non_blocking=True)
            outputs = model(images)
            preds = outputs.argmax(dim=1)

            # Move back to CPU: sklearn works on plain lists, not GPU tensors.
            all_true.extend(labels.tolist())
            all_pred.extend(preds.cpu().tolist())

    return all_true, all_pred


def print_confusion(matrix, classes):
    """Print the confusion matrix with row and column labels."""
    width = max(len(c) for c in classes) + 2

    header = " " * width + "".join(f"{c:>{width}}" for c in classes)
    print("\nConfusion matrix — rows are TRUE, columns are PREDICTED\n")
    print(header)
    for i, name in enumerate(classes):
        row = "".join(f"{matrix[i][j]:>{width}}" for j in range(len(classes)))
        print(f"{name:<{width}}{row}")


def main():
    args = parse_args()

    checkpoint_path = CHECKPOINT_DIR / f"{args.run}.pth"
    if not checkpoint_path.exists():
        available = sorted(p.name for p in CHECKPOINT_DIR.glob("*.pth"))
        raise SystemExit(
            f"No checkpoint at {checkpoint_path}\n"
            f"Available: {', '.join(available) if available else '(none)'}"
        )

    device = get_device()

    checkpoint = torch.load(CHECKPOINT, map_location=device, weights_only=False)
    classes = checkpoint["classes"]

    print(f"Checkpoint from epoch {checkpoint['epoch']}, "
          f"saved val acc {checkpoint['val_acc']:.3f}")
    print(f"Classes: {classes}")

    model = build_model(num_classes=len(classes))
    model.load_state_dict(checkpoint["model_state"])
    model = model.to(device)

    # Same seed as training, so this is the identical validation split —
    # these are images the model has never been trained on.
    _, val_loader, _ = build_dataloaders()

    y_true, y_pred = collect_predictions(model, val_loader, device)

    print(f"\nEvaluated {len(y_true)} validation images")

    print("\n" + classification_report(
        y_true, y_pred,
        target_names=classes,
        digits=3,
        zero_division=0,
    ))

    matrix = confusion_matrix(y_true, y_pred)
    print_confusion(matrix, classes)

    print("\nPredictions made per class:")
    for idx, name in enumerate(classes):
        n = sum(1 for p in y_pred if p == idx)
        print(f"  {name:<8} predicted {n:>4} times")

    if "slug" in classes and "spot" in classes:
        s, p = classes.index("slug"), classes.index("spot")
        boundary = int(matrix[s][p] + matrix[p][s])
        total_errors = int(matrix.sum() - matrix.diagonal().sum())
        if total_errors:
            print(f"\nslug/spot confusion: {boundary} of {total_errors} errors "
                  f"({100 * boundary / total_errors:.1f}%)")
if __name__ == "__main__":
    main()