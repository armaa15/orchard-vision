"""

inspect_errors.py — list which validation images the model gets wrong.
Run from inside ml/ with the venv active: python inspect_errors.py

"""

from pathlib import Path
from data import build_datasets
from model import build_model, get_device

import torch

CHECKPOINT = Path(__file__).parent / "checkpoints" / "baseline_best.pth"

def main():
    device = get_device()
    checkpoint = torch.load(CHECKPOINT, map_location=device, weights_only=False)
    classes = checkpoint["classes"]

    model = build_model(num_classes=len(classes))
    model.load_state_dict(checkpoint["model_state"])
    model = model.to(device)
    model.eval()

    # build_datasests instead of build_dataloaders because a subset lets us reach the underlying 
    # ImageFolder and recover the file path for each index, not a tensor.
    _, val_ds, _ = build_datasets()

    mistakes = []

    with torch.no_grad():
        for position, database_index in enumerate(val_ds.indices):
            image, true_label = val_ds[position]

            #The model expects a batch, unsqueeze(0) turns a single image tensor [3, 224, 224]
            # into a batch tensor with a single image [1, 3, 224, 224]
            batch = image.unsqueeze(0).to(device)
            logits = model(batch)
            predicted = logits.argmax(dim=1).item()

            if predicted != true_label:
                path = val_ds.dataset.samples[database_index][0]
                mistakes.append((
                    Path(path).name,
                    classes[true_label],
                    classes[predicted]
                ))

    print(f"{len(mistakes)} mistakes out of {len(val_ds)} validation image\n")

    for filename, truth, guess in sorted(mistakes, key = lambda m: (m[1], m[2])):
        print(f" {filename:<20} true={truth:<8} predicted={guess}")

if __name__ == "__main__":
    main()
    
