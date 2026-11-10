"""Bounded public-URL Markdown capture. No browser or crawler is silently launched."""

import ipaddress
import json
import socket
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

MAX_BYTES = 2_000_000


class AcquisitionError(RuntimeError):
    pass


def validate_public_url(url):
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Use a public HTTPS URL without credentials")
    if parsed.port not in (None, 443):
        raise ValueError("Only the default HTTPS port is supported")
    if parsed.query or parsed.fragment:
        raise ValueError("V1 capture requires a URL without query strings or fragments; do not send signed/private URLs")
    if parsed.hostname.lower() == "localhost" or parsed.hostname.lower().endswith((".local", ".internal", ".localhost")):
        raise ValueError("Local/internal destinations are not supported")
    try:
        addresses = [ipaddress.ip_address(parsed.hostname)]
    except ValueError:
        try:
            addresses = [ipaddress.ip_address(a[4][0]) for a in socket.getaddrinfo(parsed.hostname, 443, type=socket.SOCK_STREAM)]
        except OSError as error:
            raise ValueError("Destination DNS could not be verified") from error
    if not addresses or any(not address.is_global for address in addresses):
        raise ValueError("Destination must resolve only to public addresses")
    return url


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise AcquisitionError("Redirect requires explicit inspection; automatic redirects are disabled")


def post_json(url, payload, headers=None, timeout=45):
    request = Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json", **(headers or {})}, method="POST")
    try:
        with build_opener(NoRedirect).open(request, timeout=timeout) as response:
            data = response.read(MAX_BYTES + 1)
            if len(data) > MAX_BYTES:
                raise AcquisitionError("Response exceeded the capture limit")
            return data.decode("utf-8"), dict(response.headers)
    except HTTPError as error:
        # Never log request headers, response bodies, or credentials in errors.
        raise AcquisitionError(f"Provider returned HTTP {error.code}; no automatic retry") from None
    except (URLError, TimeoutError, UnicodeError, OSError):
        raise AcquisitionError("Provider connection or decoding failed; no automatic retry") from None


def capture_markdown(url, public_confirmed=False):
    if not public_confirmed:
        raise ValueError("Confirm the URL is public before sending it to markdown.new")
    validate_public_url(url)
    text, headers = post_json("https://markdown.new/", {"url": url, "method": "auto", "retain_images": False})
    content_type = next((v for k, v in headers.items() if k.lower() == "content-type"), "")
    if "text/markdown" not in content_type.lower() and "text/plain" not in content_type.lower():
        raise AcquisitionError("Expected Markdown/text, received another content type; inspect manually")
    if not text.strip():
        raise AcquisitionError("Empty extraction; record as failed rather than evidence")
    return text, {k: v for k, v in headers.items() if k.lower() in ("content-type", "x-markdown-tokens", "x-rate-limit-remaining")}
