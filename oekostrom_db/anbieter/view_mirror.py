"""
Views for mirroring content from the RoWo homepage to our app in order to show the same layout
"""

import logging
import mimetypes
import urllib.parse
from pathlib import Path

import httpx
from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse
from django.utils.encoding import smart_str

logger = logging.getLogger(__name__)


def theme(request: HttpRequest, file_path: str) -> HttpResponse:  # noqa ARG001
    return mirror(request, f"themes/{file_path}")


def mirror(request: HttpRequest, file_path: str) -> HttpResponse:  # noqa: ARG001
    # Ignore query parameters (everything after the "?")
    file_path = file_path.split("?")[0]

    # Convert to Path object for easier path manipulation
    local_file_path = Path(settings.APP_STATIC_ROOT) / file_path

    # If file already exists, serve it
    if local_file_path.exists():
        return serve_local_file(local_file_path)

    # If not, download the file from the external URL
    try:
        # Build the URL for the external resource
        external_url = f"https://www.robinwood.de/{urllib.parse.quote(file_path)}"

        # Download the file
        response = httpx.get(external_url)

        # Raise an error if the file wasn't successfully retrieved
        response.raise_for_status()

        # Ensure the directory exists
        local_dir = local_file_path.parent
        local_dir.mkdir(parents=True, exist_ok=True)

        # Write the file to STATIC_ROOT
        local_file_path.write_bytes(response.content)

        # Serve the newly downloaded file
        return serve_local_file(local_file_path)

    except httpx.HTTPError as e:
        raise Http404(f"Could not download file from {external_url}: {e}")


def serve_local_file(file_path: Path) -> HttpResponse:
    # Guess content type based on file extension (optional)
    logger.info(f"Serving {file_path}")
    content_type: str = (
        mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
    )
    extension = file_path.suffix.lower()

    if extension in [".svg", ".png", ".jpg"]:
        content_type = f"image/{extension[1:]}"

    # ensure svg are shown correctly
    if "svg" in content_type:
        content_type = "image/svg+xml"

    # Serve the file
    response = HttpResponse(file_path.read_bytes(), content_type=content_type)
    if "svg" not in content_type:
        response["Content-Disposition"] = (
            f"inline; filename={smart_str(file_path.name)}"
        )
    response["X-Content-Type-Options"] = "nosniff"
    return response
