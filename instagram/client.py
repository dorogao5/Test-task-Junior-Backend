from __future__ import annotations

import logging
from typing import Any, Self

import httpx
from decouple import config

logger = logging.getLogger(__name__)


class InstagramAPIError(Exception):
    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class InstagramClient:
    def __init__(
        self,
        access_token: str | None = None,
        user_id: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self.access_token = access_token or config("INSTAGRAM_ACCESS_TOKEN")
        self.user_id = user_id or config("INSTAGRAM_USER_ID")
        self.base_url = base_url or config("INSTAGRAM_BASE_URL")
        self._client = httpx.Client(base_url=self.base_url, timeout=15.0)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def _request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        response = self._client.request(method, url, **kwargs)
        if response.is_error:
            message = self._extract_error_message(response)
            logger.error(
                "Instagram API error: %s %s -> %d %s",
                method, url, response.status_code, message,
            )
            raise InstagramAPIError(message, response.status_code)
        return response

    @staticmethod
    def _extract_error_message(response: httpx.Response) -> str:
        try:
            payload = response.json()
        except ValueError:
            return response.text or "Instagram API request failed"

        if isinstance(payload, dict):
            error = payload.get("error")
            if isinstance(error, dict):
                message = error.get("message")
                if isinstance(message, str):
                    return message

            message = payload.get("message")
            if isinstance(message, str):
                return message

        return response.text or "Instagram API request failed"

    def get_all_media(self) -> list[dict[str, Any]]:
        """Fetch all media pages for the configured Instagram user."""
        media_items: list[dict[str, Any]] = []
        url = f"/{self.user_id}/media"
        params: dict[str, Any] | None = {
            "fields": "id,caption,media_type,timestamp",
            "access_token": self.access_token,
        }

        while True:
            response = self._request("GET", url, params=params)
            payload = response.json()

            if not isinstance(payload, dict):
                break

            data = payload.get("data", [])
            if isinstance(data, list):
                media_items.extend(item for item in data if isinstance(item, dict))

            paging = payload.get("paging")
            next_url = paging.get("next") if isinstance(paging, dict) else None

            if not isinstance(next_url, str) or not next_url:
                break

            # next_url is an absolute URL; httpx.Client uses it as-is,
            # overriding base_url. Params are already embedded in the URL.
            url = next_url
            params = None

        return media_items

    def post_comment(self, instagram_media_id: str, text: str) -> dict[str, Any]:
        """Post a comment for a media object and return API response payload."""
        response = self._request(
            "POST",
            f"/{instagram_media_id}/comments",
            data={"message": text, "access_token": self.access_token},
        )
        payload = response.json()
        if isinstance(payload, dict):
            return payload
        return {}
