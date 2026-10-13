"""
fraud_detection.py
==================
Hands-On Assignment 4 (MSCS-633): Fraud Detection using PyOD AutoEncoder.

Uses an unsupervised deep-learning AutoEncoder to detect anomalies in
the Kaggle credit-card-transactions dataset.  The AutoEncoder learns to
reconstruct normal transactions; transactions with high reconstruction
error are flagged as potential fraud.

Usage
-----
    pip install -r requirements.txt
    python fraud_detection.py

Dataset
-------
The script downloads the anonymized credit-card dataset automatically
via kagglehub.  If download fails, place `creditcard.csv` in the
`data/` directory manually from:
https://www.kaggle.com/datasets/whenamancodes/fraud-detection
"""

import os
import sys
import warnings

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
    precision_recall_curve,
    auc,
)
from pyod.models.auto_encoder import AutoEncoder
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

# ── Paths ────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CSV_PATH = os.path.join(DATA_DIR, "creditcard.csv")

# ── Hyper-parameters ─────────────────────────────────────────────────
HIDDEN_NEURONS = [25, 15, 10, 15, 25]
EPOCHS = 30
BATCH_SIZE = 64
RANDOM_STATE = 42
TEST_SIZE = 0.2


def download_dataset():
    """Download the Kaggle credit-card fraud dataset via kagglehub."""
    if os.path.isfile(CSV_PATH):
        print(f"Dataset already present at {CSV_PATH}")
        return

    print("Downloading dataset from Kaggle...")
    try:
        import kagglehub

        path = kagglehub.dataset_download("whenamancodes/fraud-detection")
        # kagglehub returns the cache directory; find the CSV inside it
        for root, _, files in os.walk(path):
            for f in files:
                if f.lower() == "creditcard.csv":
                    import shutil

                    os.makedirs(DATA_DIR, exist_ok=True)
                    shutil.copy2(os.path.join(root, f), CSV_PATH)
                    print(f"Dataset saved to {CSV_PATH}")
                    return
        raise FileNotFoundError("creditcard.csv not found in download")
    except Exception as exc:
        print(f"Auto-download failed: {exc}")
        print("Please download creditcard.csv manually from:")
        print("https://www.kaggle.com/datasets/whenamancodes/fraud-detection")
        print(f"and place it in: {DATA_DIR}")
        sys.exit(1)


def load_and_explore(path):
    """Load the dataset and print summary statistics."""
    df = pd.read_csv(path)
    print(f"\nDataset shape: {df.shape[0]:,} rows x {df.shape[1]} columns")
    print(f"\nClass distribution:")
    counts = df["Class"].value_counts()
    print(f"  Normal (0): {counts[0]:>7,}")
    print(f"  Fraud  (1): {counts[1]:>7,}")
    print(f"  Fraud ratio: {df['Class'].mean():.4%}")
    print(f"\nFeature summary (first 5 columns):")
    print(df.iloc[:, :5].describe().round(2).to_string())
    return df


def preprocess(df):
    """Scale Amount and Time, then split into train/test sets."""
    scaler = StandardScaler()
    df["Amount_scaled"] = scaler.fit_transform(df[["Amount"]])
    df["Time_scaled"] = scaler.fit_transform(df[["Time"]])

    # Use V1-V28 plus the two scaled columns; drop raw Amount, Time, Class
    feature_cols = [c for c in df.columns if c not in ("Class", "Amount", "Time")]
    X = df[feature_cols].values
    y = df["Class"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    print(f"\nTraining set : {X_train.shape[0]:,} samples  "
          f"(fraud: {y_train.sum():,})")
    print(f"Test set     : {X_test.shape[0]:,} samples  "
          f"(fraud: {y_test.sum():,})")
    return X_train, X_test, y_train, y_test


def train_autoencoder(X_train, contamination):
    """Build and train the PyOD AutoEncoder model.

    The AutoEncoder compresses input features into a lower-dimensional
    latent space and then reconstructs them.  Transactions that cannot
    be reconstructed accurately (high reconstruction error) are flagged
    as anomalies.
    """
    print(f"\nAutoEncoder architecture: {HIDDEN_NEURONS}")
    print(f"Epochs: {EPOCHS}, Batch size: {BATCH_SIZE}")
    print(f"Contamination (fraud ratio): {contamination:.5f}")

    model = AutoEncoder(
        hidden_neuron_list=HIDDEN_NEURONS,
        epoch_num=EPOCHS,
        batch_size=BATCH_SIZE,
        contamination=contamination,
        random_state=RANDOM_STATE,
        verbose=1,
    )
    model.fit(X_train)
    print("AutoEncoder training complete.")
    return model


def evaluate(model, X_test, y_test):
    """Generate predictions and print evaluation metrics."""
    y_pred = model.predict(X_test)          # binary labels
    scores = model.decision_function(X_test)  # anomaly scores

    print("\n" + "=" * 55)
    print("  MODEL EVALUATION RESULTS")
    print("=" * 55)
    print("\nClassification Report:")
    print(classification_report(
        y_test, y_pred, target_names=["Normal", "Fraud"]
    ))

    cm = confusion_matrix(y_test, y_pred)
    print("Confusion Matrix:")
    print(f"  TN={cm[0, 0]:>6,}   FP={cm[0, 1]:>5,}")
    print(f"  FN={cm[1, 0]:>6,}   TP={cm[1, 1]:>5,}")

    roc = roc_auc_score(y_test, scores)
    prec, rec, _ = precision_recall_curve(y_test, scores)
    pr = auc(rec, prec)
    print(f"\nROC-AUC Score : {roc:.4f}")
    print(f"PR-AUC Score  : {pr:.4f}")

    return y_pred, scores, cm


def plot_results(y_test, scores, cm, output_dir):
    """Save a four-panel evaluation figure."""
    os.makedirs(output_dir, exist_ok=True)

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(
        "Fraud Detection with PyOD AutoEncoder — MSCS-633",
        fontsize=14, fontweight="bold",
    )

    # 1 ── Confusion matrix heatmap
    ax = axes[0, 0]
    im = ax.imshow(cm, cmap="Blues", aspect="auto")
    ax.set_title("Confusion Matrix")
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(["Normal", "Fraud"])
    ax.set_yticklabels(["Normal", "Fraud"])
    for i in range(2):
        for j in range(2):
            color = "white" if cm[i, j] > cm.max() / 2 else "black"
            ax.text(j, i, f"{cm[i, j]:,}", ha="center", va="center",
                    color=color, fontsize=13)

    # 2 ── Anomaly-score distribution
    ax = axes[0, 1]
    ax.hist(scores[y_test == 0], bins=50, alpha=0.7,
            label="Normal", color="steelblue")
    ax.hist(scores[y_test == 1], bins=50, alpha=0.7,
            label="Fraud", color="coral")
    ax.set_title("Anomaly Score Distribution")
    ax.set_xlabel("Reconstruction Error (Anomaly Score)")
    ax.set_ylabel("Count")
    ax.legend()

    # 3 ── ROC curve
    fpr, tpr, _ = roc_curve(y_test, scores)
    roc_val = roc_auc_score(y_test, scores)
    ax = axes[1, 0]
    ax.plot(fpr, tpr, color="steelblue", lw=2,
            label=f"ROC-AUC = {roc_val:.4f}")
    ax.plot([0, 1], [0, 1], "k--", lw=1)
    ax.set_title("ROC Curve")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.legend(loc="lower right")

    # 4 ── Precision-Recall curve
    prec, rec, _ = precision_recall_curve(y_test, scores)
    pr_val = auc(rec, prec)
    ax = axes[1, 1]
    ax.plot(rec, prec, color="coral", lw=2,
            label=f"PR-AUC = {pr_val:.4f}")
    ax.set_title("Precision-Recall Curve")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.legend(loc="upper right")

    plt.tight_layout()
    save_path = os.path.join(output_dir, "results.png")
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\nPlots saved to {save_path}")


def main():
    """Run the full fraud-detection pipeline."""
    print("=" * 55)
    print("  FRAUD DETECTION USING PYOD AUTOENCODER")
    print("  MSCS-633 — Advance Artificial Intelligence")
    print("=" * 55)

    # Step 1 — Acquire data
    print("\n[1/5] Acquiring dataset...")
    download_dataset()

    # Step 2 — Load and explore
    print("\n[2/5] Loading dataset...")
    df = load_and_explore(CSV_PATH)

    # Step 3 — Preprocess
    print("\n[3/5] Preprocessing...")
    X_train, X_test, y_train, y_test = preprocess(df)

    # Step 4 — Train
    print("\n[4/5] Training AutoEncoder...")
    contamination = y_train.mean()
    model = train_autoencoder(X_train, contamination)

    # Step 5 — Evaluate and visualize
    print("\n[5/5] Evaluating model...")
    y_pred, scores, cm = evaluate(model, X_test, y_test)
    plot_results(y_test, scores, cm, OUTPUT_DIR)

    print("\n" + "=" * 55)
    print("  EXPERIMENT COMPLETE")
    print("=" * 55)


if __name__ == "__main__":
    main()
