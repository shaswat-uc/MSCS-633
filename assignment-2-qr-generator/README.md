# Hands-On Assignment 2 — AI QR Code Generator

A small Python application that generates a QR (Quick Response) code image from a
URL. By default it encodes the Biox Systems website
(https://www.bioxsystems.com/), but any URL can be supplied.

## Requirements
- Python 3.7+
- The [`qrcode`](https://pypi.org/project/qrcode/) library (with Pillow)

## Setup
Install the dependencies listed in the manifest file:

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Use the default URL (Biox Systems), save to qrcode.png
python qr_generator.py

# Encode a specific URL
python qr_generator.py --url https://www.example.com

# Encode a URL and choose the output filename
python qr_generator.py --url https://www.example.com --output my_qr.png
```

If you run the program without `--url`, it will prompt you to type one
(pressing Enter accepts the default Biox Systems URL).

## Output
The program writes a PNG image (default: `qrcode.png`) containing the QR code.
Scanning it with a phone camera opens the encoded URL.

![Sample QR code for the Biox Systems website](qrcode.png)

## Files
| File | Purpose |
|------|---------|
| `qr_generator.py` | Application source code |
| `requirements.txt` | Manifest of Python dependencies |
| `qrcode.png` | Sample generated output |
