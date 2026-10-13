# Assignment 4 — Fraud Detection with PyOD AutoEncoder

MSCS-633: Advance Artificial Intelligence

## Overview

Unsupervised deep-learning fraud detection using PyOD's AutoEncoder on the
Kaggle credit-card transactions dataset. The AutoEncoder learns to reconstruct
normal transactions; high reconstruction error flags potential fraud.

## Setup

```bash
pip install -r requirements.txt
python fraud_detection.py
```

The script downloads the dataset automatically via `kagglehub`.
If auto-download fails, place `creditcard.csv` in the `data/` directory from:
https://www.kaggle.com/datasets/whenamancodes/fraud-detection

## Output

Evaluation metrics and a four-panel plot (`output/results.png`) are generated
automatically.
