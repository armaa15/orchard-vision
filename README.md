# orchard-vision
Full-stack orchard management app with ML leaf-disease detection for a 200-tree pear orchard.

## The problem

The orchard is tracked on paper. There's no way to see whether a disease is
spreading, or which trees are declining year over year. Six trees in the same
section with the same infection is information a notebook can't surface.

## What it does

- **Tree registry** — records for each tree: section, variety, planting year
- **Observation log** — dated entries per tree, with photo upload
- **Disease classification** — upload a leaf photo, get a predicted disease and
  confidence score, stored against that tree
- **Dashboard** — health trends over time and spatial clustering of detections

## Stack

**Frontend** React, TypeScript, Vite, Tailwind
**Backend** FastAPI, Pydantic, SQLAlchemy
**Database** PostgreSQL
**ML** PyTorch, transfer learning on a pretrained CNN
**Infrastructure** Docker, Railway (backend), Vercel (frontend)

## Status

In active development. Built July–August 2026.
