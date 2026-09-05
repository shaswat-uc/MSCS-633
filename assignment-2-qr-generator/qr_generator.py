"""
qr_generator.py
================
Hands-On Assignment 2 (MSCS-633): AI QR Code Generator.

This application takes a URL as input and produces a QR (Quick Response) code
image that, when scanned, opens that URL. By default it encodes the Biox
Systems website (https://www.bioxsystems.com/), but any URL may be supplied.

The QR code is generated with the `qrcode` library (which uses Pillow to render
the PNG image).

Usage
-----
    # Use the default URL (Biox Systems) and default output file:
    python qr_generator.py

    # Provide a specific URL:
    python qr_generator.py --url https://www.example.com

    # Provide a URL and a custom output filename:
    python qr_generator.py --url https://www.example.com --output my_qr.png

    # If no --url is given, the program will interactively ask for one.

Author: Shaswat Dharaiya
Course: MSCS-633, University of the Cumberlands
"""

import argparse
import sys

import qrcode

# The default website to encode when the user does not supply one.
DEFAULT_URL = "https://www.bioxsystems.com/"
# The default filename for the generated QR code image.
DEFAULT_OUTPUT = "qrcode.png"


def is_valid_url(url: str) -> bool:
    """Perform a light-weight check that the string looks like a web URL.

    A full URL validator is out of scope for this assignment; we simply make
    sure the value is non-empty and starts with an http/https scheme so that
    the scanned QR code opens correctly in a browser.
    """
    url = url.strip()
    return url.startswith("http://") or url.startswith("https://")


def generate_qr_code(url: str, output_file: str) -> str:
    """Generate a QR code for `url` and save it to `output_file`.

    Parameters
    ----------
    url : str
        The URL/text to encode inside the QR code.
    output_file : str
        The path of the PNG file to write.

    Returns
    -------
    str
        The path of the saved image file.
    """
    # Configure the QR code.
    #   version=None      -> let the library pick the smallest size that fits.
    #   error_correction  -> ERROR_CORRECT_H allows ~30% of the code to be
    #                        damaged/obscured and still scan reliably.
    #   box_size          -> number of pixels per QR "box" (module).
    #   border            -> width of the quiet zone (minimum is 4 per spec).
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )

    # Add the data and let the library compute the optimal size (fit=True).
    qr.add_data(url)
    qr.make(fit=True)

    # Render the QR code as an image (black modules on a white background).
    image = qr.make_image(fill_color="black", back_color="white")

    # Persist the image to disk as a PNG file.
    image.save(output_file)
    return output_file


def parse_arguments() -> argparse.Namespace:
    """Parse and return the command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate a QR code image from a URL."
    )
    parser.add_argument(
        "-u",
        "--url",
        help="The URL to encode in the QR code "
        "(defaults to the Biox Systems website).",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Output PNG filename (default: {DEFAULT_OUTPUT}).",
    )
    return parser.parse_args()


def main() -> None:
    """Program entry point: read input, validate it, and generate the QR code."""
    args = parse_arguments()

    # Determine the URL: prefer the command-line value; otherwise ask the user;
    # otherwise fall back to the default Biox Systems URL.
    url = args.url
    if not url:
        entered = input(
            f"Enter a URL to encode [default: {DEFAULT_URL}]: "
        ).strip()
        url = entered or DEFAULT_URL

    # Validate the URL before generating the code.
    if not is_valid_url(url):
        print(
            "Error: please provide a valid URL that starts with "
            "'http://' or 'https://'.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Generate the QR code and report the result to the user.
    saved_path = generate_qr_code(url, args.output)
    print(f"Success! QR code for '{url}' saved to '{saved_path}'.")


# Standard Python idiom: only run main() when executed as a script,
# not when imported as a module.
if __name__ == "__main__":
    main()
