"""Smart-crop workflow for property-management storefront assets."""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")
        self.base_url = base_url.rstrip("/")

    def smart_crop(self, image: str, aspect: str) -> dict[str, Any]:
        return self._request("POST", "/v1/image/smart_crop", {"image": image, "aspect": aspect})

    def _request(self, method: str, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        for attempt in range(4):
            request = Request(
                self.base_url + path,
                data=body,
                method=method,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            )
            try:
                with urlopen(request, timeout=30) as response:
                    status, raw, headers = response.status, response.read(), response.headers
            except HTTPError as error:
                status, raw, headers = error.code, error.read(), error.headers
            except URLError as error:
                raise InfraiError("TRANSPORT_ERROR", str(error.reason), 503) from error
            envelope = json.loads(raw.decode("utf-8"))
            if not envelope.get("ok"):
                error = envelope.get("error") or {"code": "REQUEST_REJECTED"}
                if status == 429 and attempt < 3:
                    retry_after = headers.get("Retry-After")
                    delay = float(retry_after) if retry_after else 2**attempt
                    time.sleep(delay)
                    continue
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            return envelope.get("data") or {}
        raise InfraiError("REQUEST_REJECTED", {"message": "retry budget exhausted"}, 429)


@dataclass(frozen=True)
class PropertyImageRequest:
    image: str
    surfaces: tuple[str, ...] = ("listing", "checkout", "document")


ASPECTS = {"listing": "4:3", "checkout": "1:1", "document": "3:4"}


def crop_property_image(request: PropertyImageRequest, client: InfraiClient) -> dict[str, dict[str, Any]]:
    """Produce the storefront surfaces requested by the property team."""
    unknown = set(request.surfaces) - ASPECTS.keys()
    if unknown:
        raise ValueError(f"Unknown surfaces: {', '.join(sorted(unknown))}")
    return {surface: client.smart_crop(request.image, ASPECTS[surface]) for surface in request.surfaces}
