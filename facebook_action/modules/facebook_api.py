"""This module provides the FacebookAPI class for interacting with the Facebook Graph API."""

import logging
import mimetypes
import random
import string
import traceback
from typing import Any, Dict, List, Optional, Union

import requests
from jvserve.lib.file_interface import file_interface


class FacebookAPI:
    """
    A class to interact with the Facebook Graph API for various actions such as sending messages,
    updating webhooks, and managing Facebook pages.
    """

    logger = logging.getLogger(__name__)

    def __init__(
        self,
        api_url: str,
        app_secret: str,
        app_id: str,
        page_id: str,
        access_token: str,
        verify_token: str,
        fields: Optional[str] = None,
        timeout: int = 10,
    ) -> None:
        """
        Initializes the FacebookAPI object with base URL, instance, and credentials.

        :param api_url: API base URL.
        :param app_secret: Facebook app secret.
        :param app_id: Facebook app ID.
        :param page_id: Facebook page ID.
        :param access_token: Facebook page access token.
        :param verify_token: Facebook webhook verification token.
        :param fields: Optional fields to be retrieved when fetching a page.
        :param timeout: Optional timeout in seconds for API requests.
        """
        self.api_url = api_url
        self.app_secret = app_secret
        self.app_id = app_id
        self.page_id = page_id
        self.access_token = access_token
        self.verify_token = verify_token
        self.fields = fields
        self.timeout = timeout

    def send_rest_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        json_body: Optional[Dict] = None,
    ) -> Dict:
        """Centralized method to send HTTP requests with standardized error handling."""
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            url = endpoint
        else:
            url = f"{self.api_url}{endpoint}"

        try:
            response = requests.request(
                method=method.upper(),
                url=url,
                params=params,
                data=data,
                json=json_body,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.Timeout as e:
            self.logger.error(f"Request timed out after {self.timeout} seconds: {e}")
            return {"error": f"Timeout after {self.timeout} seconds"}
        except requests.RequestException as e:
            self.logger.error(f"Request error: {str(e)}")
            error_details = (
                e.response.json() if e.response and e.response.content else None
            )
            return {"error": str(e), "details": error_details}
        except Exception as e:
            self.logger.error(f"Unexpected error: {traceback.format_exc()}")
            return {"error": str(e)}

    def parse_verification_request(self, request: Dict) -> Union[str, Dict[Any, Any]]:
        """Parses verification request payload and returns the challenge value if the token is valid."""
        try:
            hub_mode = request.get("hub.mode")
            hub_verify_token = request.get("hub.verify_token")
            hub_challenge = request.get("hub.challenge")

            if hub_verify_token == self.verify_token and hub_mode == "subscribe":
                return hub_challenge if hub_challenge is not None else ""
            return {"message": "Invalid token or mode", "code": 403}
        except Exception as e:
            self.logger.error(
                f"Unable to process verification request: {traceback.format_exc()}"
            )
            return {"error": str(e)}

    def register_session(self, webhook_url: str) -> Dict:
        """Update Facebook webhook."""
        endpoint = f"{self.app_id}/subscriptions"
        params = {"access_token": f"{self.app_id}|{self.app_secret}"}
        data = {
            "object": "page",
            "callback_url": webhook_url,
            "fields": self.fields,
            "verify_token": self.verify_token,
            "include_values": "true",
        }
        return self.send_rest_request("POST", endpoint, params=params, json_body=data)

    @staticmethod
    def parse_inbound_message(request: Dict) -> Dict:
        """Parses message request payload and returns extracted values."""
        payload = {}
        try:
            entry = request["entry"][0]
            page_id = entry["id"]
            sender_id = ""
            message_type = ""
            message = ""
            sender_name = ""
            attachments = []
            caption = ""
            parent_message_id = ""

            if "changes" in entry:
                change = entry["changes"][0]["value"]
                sender_id = change["from"]["id"]
                sender_name = change["from"]["name"]
                message_type = change["item"]
                message = change.get("message") or change.get("reaction_type")
            elif "messaging" in entry:
                messaging = entry["messaging"][0]
                sender_id = messaging["sender"]["id"]
                message_type = "message"
                message = messaging["message"].get("text")
                attachments = messaging["message"].get("attachments", [])

            payload = {
                "sender_name": sender_name,
                "sender_id": sender_id,
                "page_id": page_id,
                "message_type": message_type,
                "message": message,
                "attachments": attachments,
                "caption": caption,
                "data": request,
                "parent_message_id": parent_message_id,
            }
            return payload
        except Exception as e:
            FacebookAPI.logger.error(
                f"Facebook API: Error processing inbound message: {e}"
            )
            return {"ok": False, "error": str(e)}

    def send_text_message(self, recipient_id: str, message: str) -> Dict:
        """Send text message to a Facebook user via Messenger."""
        endpoint = f"{self.page_id}/messages"
        headers = {"Content-Type": "application/json"}
        data = {
            "recipient": {"id": recipient_id},
            "messaging_type": "RESPONSE",
            "message": {"text": message},
        }
        params = {"access_token": self.access_token}
        return self.send_rest_request(
            "POST", endpoint, headers=headers, json_body=data, params=params
        )

    def send_media(
        self,
        recipient_id: str,
        media_url: str,
        media_type: str,
    ) -> Dict:
        """Send a media message (audio, image, video, or document) to a user via Messenger."""
        endpoint = f"{self.page_id}/messages"
        headers = {"Content-Type": "application/json"}
        data = {
            "recipient": {"id": recipient_id},
            "messaging_type": "RESPONSE",
            "message": {
                "attachment": {
                    "type": media_type,
                    "payload": {"url": media_url, "is_reusable": True},
                }
            },
        }
        params = {"access_token": self.access_token}
        return self.send_rest_request(
            "POST", endpoint, headers=headers, json_body=data, params=params
        )

    def get_user_info(self, fields: str = "id,name") -> Dict:
        """Fetches user information from the Facebook Graph API."""
        endpoint = "me"
        params = {"fields": fields, "access_token": self.access_token}
        return self.send_rest_request("GET", endpoint, params=params)

    def list_all_pages(self, limit: int = 100) -> Union[List, Dict]:
        """Lists all pages managed by the user."""

        try:
            all_pages = []
            endpoint = "me/accounts"
            params = {"access_token": self.access_token, "limit": limit}

            while True:
                response = self.send_rest_request("GET", endpoint, params=params)
                if "error" in response:
                    return []
                all_pages.extend(response.get("data", []))
                paging = response.get("paging", {})
                next_page = paging.get("next")
                if not next_page:
                    break
                endpoint = next_page
                params = {}
            return all_pages
        except Exception as e:
            self.logger.error(f"Facebook API: Error listing pages: {e}")
            return {"ok": False, "error": str(e)}

    def get_page_details(
        self,
        fields: str = "id,name,about,fan_count,access_token",
    ) -> Dict:
        """Fetches details of a Facebook page."""
        endpoint = self.page_id
        params = {"fields": fields, "access_token": self.access_token}
        return self.send_rest_request("GET", endpoint, params=params)

    def post_message_to_page(self, message: str) -> Dict:
        """Posts a message to a Facebook page."""
        endpoint = f"{self.page_id}/feed"
        headers = {"Content-Type": "application/json"}
        json_data = {"message": message}
        params = {"access_token": self.access_token}
        return self.send_rest_request(
            "POST", endpoint, headers=headers, json_body=json_data, params=params
        )

    def get_page_posts(self, limit: int = 10) -> Union[List, Dict]:
        """Retrieves posts from a Facebook page. Most recent post first."""
        endpoint = f"{self.page_id}/posts"
        params = {"access_token": self.access_token, "limit": limit}
        return self.send_rest_request("GET", endpoint, params=params)

    def get_single_post(self, post_id: str) -> Dict:
        """Retrieves a single post from a Facebook page by post ID."""
        endpoint = post_id
        params = {"access_token": self.access_token}
        return self.send_rest_request("GET", endpoint, params=params)

    def comment_on_post(self, post_id: str, message: str) -> Dict:
        """Comments on a Facebook post."""
        endpoint = f"{post_id}/comments"
        params = {"message": message, "access_token": self.access_token}
        return self.send_rest_request("POST", endpoint, params=params)

    def post_images_to_page(self, image_urls: List[str], caption: str) -> Dict:
        """Uploads multiple photos to a Facebook page using URLs."""

        try:
            image_ids = []
            for image_url in image_urls:
                endpoint = f"{self.page_id}/photos"
                params = {
                    "access_token": self.access_token,
                    "url": image_url,
                    "published": "false",
                }
                response = self.send_rest_request("POST", endpoint, params=params)
                if "error" not in response:
                    image_ids.append(response.get("id"))

            if not image_ids:
                return {"error": "Failed to upload any images"}

            endpoint = f"{self.page_id}/feed"
            params = {"access_token": self.access_token}
            json_data = {
                "message": caption,
                "attached_media": [{"media_fbid": _id} for _id in image_ids],
            }
            return self.send_rest_request(
                "POST", endpoint, params=params, json_body=json_data
            )
        except Exception as e:
            self.logger.error(f"Facebook API: Error posting images: {e}")
            return {"ok": False, "error": str(e)}

    def post_videos_to_page(
        self, title: str, caption: str, video_urls: List[str]
    ) -> Dict:
        """Uploads multiple videos to a Facebook page using URLs."""
        try:
            video_ids = []
            for video_url in video_urls:
                endpoint = f"{self.page_id}/videos"
                params = {
                    "access_token": self.access_token,
                    "title": title,
                    "file_url": video_url,
                }
                response = self.send_rest_request("POST", endpoint, params=params)
                if "error" not in response:
                    video_ids.append(response.get("id"))

            if not video_ids:
                return {"error": "Failed to upload any videos"}

            endpoint = f"{self.page_id}/feed"
            params = {"access_token": self.access_token}
            json_data = {
                "message": caption,
                "attached_media": [{"media_fbid": _id} for _id in video_ids],
            }
            return self.send_rest_request(
                "POST", endpoint, params=params, json_body=json_data
            )
        except Exception as e:
            self.logger.error(f"Facebook API: Error posting videos: {e}")
            return {"ok": False, "error": str(e)}

    @staticmethod
    def get_mime_type(
        file_path: Optional[str] = None,
        url: Optional[str] = None,
        mime_type: Optional[str] = None,
    ) -> Optional[Dict]:
        """Determine the MIME type of a file or URL and categorize it."""
        detected_mime_type = None

        if file_path:
            detected_mime_type, _ = mimetypes.guess_type(file_path)
        elif url:
            try:
                response = requests.head(url, allow_redirects=True)
                detected_mime_type = response.headers.get("Content-Type")
            except requests.RequestException:
                return None
        else:
            detected_mime_type = mime_type

        image_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        document_types = ["application/pdf", "text/plain"]
        audio_types = ["audio/mpeg", "audio/wav"]
        video_types = ["video/mp4", "video/quicktime"]

        if detected_mime_type in image_types:
            return {"file_type": "image", "mime": detected_mime_type}
        elif detected_mime_type in document_types:
            return {"file_type": "document", "mime": detected_mime_type}
        elif detected_mime_type in audio_types:
            return {"file_type": "audio", "mime": detected_mime_type}
        elif detected_mime_type in video_types:
            return {"file_type": "video", "mime": detected_mime_type}
        else:
            return {"file_type": "unknown", "mime": detected_mime_type}

    def post_media_to_page(self, caption: str, media_urls: List[Dict]) -> Dict:
        """Posts media (images or videos) to a Facebook page using URLs."""

        try:

            media_ids = []
            for media in media_urls:
                media_url = media.get("url")
                mime_info = self.get_mime_type(url=media_url)
                media_type = mime_info.get("file_type") if mime_info else None

                if media_type == "video":
                    endpoint = f"{self.page_id}/videos"
                    params = {
                        "access_token": self.access_token,
                        "file_url": media_url,
                    }
                elif media_type == "image":
                    endpoint = f"{self.page_id}/photos"
                    params = {
                        "access_token": self.access_token,
                        "url": media_url,
                        "published": "false",
                    }
                else:
                    continue

                response = self.send_rest_request("POST", endpoint, params=params)
                if "error" not in response:
                    media_ids.append(response.get("id"))

            if not media_ids:
                return {"error": "No valid media uploaded"}

            endpoint = f"{self.page_id}/feed"
            params = {"access_token": self.access_token}
            json_data = {
                "message": caption,
                "attached_media": [{"media_fbid": _id} for _id in media_ids],
            }
            return self.send_rest_request(
                "POST", endpoint, params=params, json_body=json_data
            )
        except Exception as e:
            self.logger.error(f"Facebook API: Error posting media: {e}")
            return {"ok": False, "error": str(e)}

    def get_post_comments(self, post_id: str, limit: int = 10) -> Union[List, Dict]:
        """Retrieves comments on a Facebook post."""
        endpoint = f"{post_id}/comments"
        params = {"access_token": self.access_token, "limit": limit}
        return self.send_rest_request("GET", endpoint, params=params)

    def reply_to_comment(self, comment_id: str, message: str) -> Dict:
        """Replies to a comment on a Facebook post."""
        endpoint = f"{comment_id}/comments"
        params = {"message": message, "access_token": self.access_token}
        return self.send_rest_request("POST", endpoint, params=params)

    def reply_to_comment_with_attachment(
        self, comment_id: str, attachment_url: str
    ) -> Dict:
        """Replies to a comment with an attachment."""
        endpoint = f"{comment_id}/comments"
        data = {"attachment_url": attachment_url, "access_token": self.access_token}
        return self.send_rest_request("POST", endpoint, data=data)

    def update_comment(self, comment_id: str, message: str) -> Dict:
        """Updates a comment on a Facebook post."""
        endpoint = comment_id
        data = {"message": message, "access_token": self.access_token}
        return self.send_rest_request("POST", endpoint, data=data)

    def like_comment(self, comment_id: str) -> Dict:
        """Likes a comment on a Facebook post."""
        endpoint = f"{comment_id}/likes"
        params = {"access_token": self.access_token}
        return self.send_rest_request("POST", endpoint, params=params)

    def get_reactions(self, post_id: str) -> Union[List, Dict]:
        """Retrieves reactions on a Facebook post."""
        endpoint = f"{post_id}/reactions"
        params = {"access_token": self.access_token}
        return self.send_rest_request("GET", endpoint, params=params)

    @staticmethod
    def download_file(url: str) -> Optional[str]:
        """Download a file from a URL and save it. Returns a web-accessible URL."""
        try:
            response = requests.head(url, allow_redirects=True)
            content_type = response.headers.get("Content-Type", "")
            extension = mimetypes.guess_extension(content_type.split(";")[0])
            if not extension:
                return None

            filename = (
                "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
                + extension
            )
            output_path = f"fb/{filename}"

            response = requests.get(url, stream=True)
            if response.status_code == 200:
                file_bytes = bytearray()
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file_bytes.extend(chunk)
                file_interface.save_file(output_path, bytes(file_bytes))
                return file_interface.get_file_url(output_path)
            return None
        except Exception:
            return None

    def share_facebook_post(self, post_id: str) -> Dict:
        """Fetches the permalink URL of a Facebook post."""
        endpoint = post_id
        params = {"fields": "permalink_url", "access_token": self.access_token}
        response = self.send_rest_request("GET", endpoint, params=params)
        if "permalink_url" in response:
            return {"status": "success", "data": response["permalink_url"]}
        return {"status": "error", "message": response.get("error", "Unknown error")}
