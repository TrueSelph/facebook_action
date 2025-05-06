import:py os;
import:py traceback;
import:py logging;
import:py from logging { Logger }
import:py from modules.facebook_api { FacebookAPI }
import:py from jivas.agent.modules.agentlib.utils { Utils }
import:py from jvserve.lib.agent_interface { AgentInterface }
import:jac from jivas.agent.action.action { Action }
import:jac from jivas.agent.memory.interaction_response { MessageType }


node FacebookAction :Action: {
    # houses configurations per agent for facebook api communications provided by Facebook api

    # set up logger
    static has logger:Logger = logging.getLogger(__name__);

    has api_url:str = 'https://graph.facebook.com/v21.0/';
    has base_url:str = "";
    has webhook_url:str = "";
    has app_id:str = "";
    has app_secret:str = "";
    has page_id:str = "";
    has page_access_token:str = "";
    has subscribed_fields: str = "feed,messages";
    has webhook_verify_token:str = "123";
    has chunk_length:int = 1024;
    has use_pushname:bool = True; # use the WhatsApp push name as the user name
    has request_timeout:int = 10; # the length of time this action waits for api to complete request


    can on_enable() {
        # check if enabled
        if(self.enabled) {
            # register polls webhook
            self.enabled = self.on_register();
        }
    }

    can on_register() -> bool {
        if (not self.base_url) {
            # default to jivas base url in environment
            self.base_url = os.environ.get('JIVAS_BASE_URL');
        }

        if(self.enabled) {
            # setup procedure for webhook registration on Facebook api
            agent_id = self.get_agent().id;
            module_root = self.get_module_root();

            # generate webhook key
            webhook_key = AgentInterface.encrypt_webhook_key(agent_id=agent_id, module_root=module_root, walker="facebook_interact");

            if(self.base_url and webhook_key) {
                # complete the full webhook url
                self.webhook_url = f'{self.base_url}/webhook/{webhook_key}';
                self.logger.debug(f'Facebook webhook url: {self.webhook_url}');

                result = self.api().update_webhook(webhook=self.webhook_url);
                self.logger.warning(f'Facebook webhook registration result: {result}');
                return True;
            } else {
                self.logger.error('unable to generate webhook url for Facebook, missing required parameters');
            }
        } else {
            self.logger.warning('facebook action is disabled');
        }

        return False;
    }

    # --------------- FacebookAPI ----------------

    can api() -> FacebookAPI {
        # load the api instance

        return FacebookAPI(
            api_url=self.api_url,
            app_secret=self.app_secret,
            app_id=self.app_id,
            page_id=self.page_id,
            verify_token=self.webhook_verify_token,
            access_token=self.page_access_token,
            fields=self.subscribed_fields,
            timeout=self.request_timeout
        );

    }

    can sanitize_message(message:str) {
        return message.replace("**", "*").replace("<br/>", "\n").replace("<b>", "*").replace("</b>", "*");
    }

    can verify_request(request:dict) -> str {
        return self.api().parse_verification_request(request=request);
    }

    can send_message(session_id:str, message:InteractionMessage) {
        # processes an agent response payload format and sends an Facebook message to a specified session_id via the action
        if(message and session_id) {
            parent_message_id = message.get_meta('parent_message_id');

            if (message.get_type() == MessageType.SILENCE.value) {}
            elif(message.get_type() == MessageType.TEXT.value) {
                content = self.sanitize_message(message = message.get_content());
                outgoing = Utils.chunk_long_message(message=content, max_length = self.chunk_length, chunk_length = self.chunk_length);

                for chunk in outgoing {
                    self.api().send_text_message(recipient_id=session_id, message=chunk);
                }
            } elif(message.get_type() == MessageType.MEDIA.value) {
                # sending media
                mime_type = Utils.get_mime_type(mime_type=message.mime);
                if(mime_type['file_type'] == "document") {
                    self.api().send_media(recipient_id= session_id, media_url=message.data.get('url'), media_type="document");
                }elif(mime_type['file_type'] == "image") {
                    self.api().send_media(recipient_id= session_id, media_url=message.data.get('url'), media_type="image");
                }elif(mime_type['file_type'] == "video") {
                    self.api().send_media(recipient_id= session_id, media_url=message.data.get('url'), media_type="video");
                }

                # sending caption
                caption = self.sanitize_message(message = message.get_content());
                if(caption) {
                    self.api().send_text_message(recipient_id=session_id, message=caption);
                }
            } elif(message.get_type() == MessageType.MULTI.value) {
                for message_item in message.content {
                    if(message_item.get_type() == MessageType.TEXT.value) {
                        message = self.sanitize_message(message = message_item.get_content());
                        outgoing = Utils.chunk_long_message(message=message, max_length = self.chunk_length, chunk_length = self.chunk_length);

                        for chunk in outgoing {
                            self.api().send_text_message(recipient_id=session_id, message=chunk);
                        }
                    } elif(message_item.get_type() == MessageType.MEDIA.value) {
                        # sending media
                        mime_type = Utils.get_mime_type(mime_type=message_item.mime);
                        if(mime_type['file_type'] == "document") {
                            self.api().send_media(recipient_id= session_id, media_url=message_item.data.get('url'), media_type="document");
                        } elif(mime_type['file_type'] == "image") {
                            self.api().send_media(recipient_id= session_id, media_url=message_item.data.get('url'), media_type="image");
                        } elif(mime_type['file_type'] == "video") {
                            self.api().send_media(recipient_id= session_id, media_url=message_item.data.get('url'), media_type="video");
                        }
                        # sendign caption
                        caption = self.sanitize_message(message = message_item.get_content());
                        if(caption) {
                            self.api().send_text_message(recipient_id=session_id, message=caption);
                        }
                    }
                }
            }
        }
    }


    can broadcast_message(message:InteractionMessage, channels:list, session_id:str) {
        # processes an agent response payload format and sends an ultramsg message to all session_ids via the action

        agent_node = self.get_agent();

        if(frames := agent_node.get_memory().get_frames() ) {
            # get all frames then proceed to broadcast
            for frame_node in frames {
                if(frame_node.session_id != session_id) {
                    if(interaction_node := frame_node.get_last_interaction()) {
                        if interaction_node.channel in ['whatsapp'] {
                            self.send_message(session_id = frame_node.session_id, message=message);
                        }
                    }
                }
            }
        }
    }


    can send_media(session_id:str, media_type:str, media_url:str) -> dict {
        media_url = self.serve_file_url(media_url);
        return self.api().send_media(
            recipient_id=session_id,
            media_url=media_url,
            media_type=media_type
        );
    }

    can get_post_link(post_id:str) -> dict {
        return self.api().share_facebook_post(post_id=post_id);
    }


    can post_message(message:str, post_link:bool = True) -> dict {

        post_result = self.api().post_message_to_page(message=message);

        self.logger.warning(f"Post result: {post_result}");

        # if (post_link and post_result != None) {
        #     if post_result.get('status', 'success') != 'error' {
        #         return self.get_post_link(post_id=post_result);
        #     }
        # }

        return post_result;
    }


    can post_images(image_urls:list, caption:str, post_link:bool = True) -> dict {
        media_urls = [];
        for video_url in image_urls {
            if(url := self.serve_file_url(video_url)) {
                media_urls.append(url);
            }
        }

        post_result = self.api().post_images_to_page(image_urls=media_urls, caption=caption);

        self.logger.warning(f"Post result: {post_result}");
        # if ("error" not in post_result and post_link) {
        #     return self.get_post_link(post_id=post_result);
        # }

        return post_result;
    }


    can post_videos(video_urls:list, caption:str, title:str = "", post_link:bool = True) -> dict {
        media_urls = [];
        for video_url in video_urls {
            if(url := self.serve_file_url(video_url)) {
                media_urls.append(url);
            }
        }
        post_result = self.api().post_videos_to_page(title=title, caption=caption, video_urls=media_urls);

        self.logger.warning(f"Post result: {post_result}");
        # if ("error" not in post_result and post_link) {
        #     return self.get_post_link(post_id=post_result);
        # }

        return post_result;
    }

    can get_posts(limit:int = 10) -> dict {
        return self.api().get_page_posts(limit=limit);
    }

    can get_post(post_id:str) -> dict {
        return self.api().get_single_post(post_id=post_id);
    }


    can get_comments(post_id: str, limit: int = 10) -> dict {
        return self.api().get_post_comments(post_id=post_id, limit=limit);
    }


    can comment_on_post(post_id: str, message: str) -> dict {
        return self.api().comment_on_post(post_id=post_id, message=message);
    }


    can update_comment(comment_id: str, message: str) -> dict {
        return self.api().update_comment(comment_id=comment_id, message=message);
    }


    can like_comment(comment_id: str) -> dict {
        return self.api().like_comment(comment_id=comment_id);
    }


    can get_reactions(post_id: str) -> dict {
        return self.api().get_reactions(post_id=post_id);
    }


    can reply_to_comment(comment_id: str, message: str) -> dict {
        return self.api().reply_to_comment(comment_id=comment_id, message=message);
    }


    can reply_to_comment_with_attachment(comment_id: str, message: str, attachment_url: str) -> dict{
        return self.api().reply_to_comment_with_attachment(comment_id=comment_id, message=message, attachment_url=attachment_url);
    }

    can serve_file_url(url:str) -> dict {
        # accepts a temporary web url of a file, downloads it and serves it from jv file service
        return self.api().download_file(url);
    }

    can healthcheck() -> Union[bool, dict] {
        try {
            # Check if the types of attributes are as expected
            if (
                self.base_url and
                self.app_id and
                self.app_secret and
                self.subscribed_fields and
                self.webhook_verify_token and
                self.webhook_url
            ) {

                # Validate the 'pages' section
                for page_name in self.pages {
                    page_info = self.pages.get(page_name);
                    if (type(page_info) != dict) {
                        # Each page entry must be a dictionary
                        return {
                            "status": False,
                            "message": "Each page entry must be represented as a JSON dictionary.",
                            "severity": "error"
                        };
                    }

                    # Ensure each page has the required keys with appropriate types
                    if (not page_info.get("page_id") or not page_info.get("page_access_token")) {
                        return {
                            "status": False,  # Missing required page details
                            "message": "Missing page details",
                            "severity": "error"
                        };
                    }
                }

                return True;  # All checks passed
            }

            return False;  # One or more type checks failed

        } except Exception as e{
            self.logger.error(f"An exception occurred in {self.label}:\n{traceback.format_exc()}\n");
            return False;
        }
    }
}