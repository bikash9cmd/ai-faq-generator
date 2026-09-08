import ipaddress
import socket
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


MAX_CONTENT_LENGTH = 2_000_000  # 2 MB
REQUEST_TIMEOUT = 10

ALLOWED_SCHEMES = {"http", "https"}


def _validate_url(url: str) -> None:
    """Validate URL and block unsafe/internal destinations."""

    parsed = urlparse(url)

    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ValueError("Only http and https URLs are allowed.")

    if not parsed.hostname:
        raise ValueError("Invalid URL. Please provide a valid URL.")

    hostname = parsed.hostname.lower()

    # Block localhost-style hostnames
    blocked_hostnames = {
        "localhost",
        "localhost.localdomain",
    }

    if hostname in blocked_hostnames:
        raise ValueError("Access to local addresses is not allowed.")

    # Resolve hostname and block private/internal IP addresses
    try:
        addresses = socket.getaddrinfo(
            hostname,
            None,
            type=socket.SOCK_STREAM,
        )

        for address in addresses:
            ip = ipaddress.ip_address(address[4][0])

            if (
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_reserved
                or ip.is_multicast
            ):
                raise ValueError(
                    "Access to private or internal addresses is not allowed."
                )

    except socket.gaierror:
        raise ValueError("Unable to resolve the provided URL.")


def extract_content_from_url(url: str) -> str:
    """
    Fetch a webpage and extract readable text safely.
    """

    _validate_url(url)

    try:
        response = requests.get(
            url,
            timeout=REQUEST_TIMEOUT,
            headers={
                "User-Agent": "AI-FAQ-Generator/1.0"
            },
            allow_redirects=True,
        )

        response.raise_for_status()

    except requests.Timeout:
        raise ValueError("The webpage took too long to respond.")

    except requests.RequestException as exc:
        raise ValueError(f"Unable to access the webpage: {exc}")

    # Only process HTML pages
    content_type = response.headers.get("content-type", "").lower()

    if "text/html" not in content_type:
        raise ValueError("The provided URL does not contain an HTML webpage.")

    # Protect the application from extremely large responses
    content_length = response.headers.get("content-length")

    if content_length:
        try:
            if int(content_length) > MAX_CONTENT_LENGTH:
                raise ValueError(
                    "The webpage is too large to process."
                )
        except ValueError:
            if content_length.isdigit():
                raise ValueError(
                    "The webpage is too large to process."
                )

    if len(response.content) > MAX_CONTENT_LENGTH:
        raise ValueError("The webpage is too large to process.")

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove elements that usually do not contain useful page content
    for element in soup([
        "script",
        "style",
        "noscript",
        "nav",
        "footer",
        "header",
        "aside",
        "form",
    ]):
        element.decompose()

    text = soup.get_text(separator=" ", strip=True)

    if not text:
        raise ValueError("No readable content found on the webpage.")

    return text
