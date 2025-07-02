# Facebook Action

![GitHub release (latest by date)](https://img.shields.io/github/v/release/TrueSelph/facebook_action)
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/TrueSelph/facebook_action/test-facebook_action.yaml)
![GitHub issues](https://img.shields.io/github/issues/TrueSelph/facebook_action)
![GitHub pull requests](https://img.shields.io/github/issues-pr/TrueSelph/facebook_action)
![GitHub](https://img.shields.io/github/license/TrueSelph/facebook_action)

JIVAS action wrapper for Facebook API communications with advanced mass messaging outbox. This action provides a wrapper for Facebook API communications using the [Facebook Developer API](https://developers.facebook.com/docs). As a core action, it simplifies and streamlines interactions with Facebook. The package is a singleton and requires the Jivas library version ^2.1.0.

## Package Information
- **Name:** `jivas/facebook_action`
- **Author:** [V75 Inc.](https://v75inc.com/)
- **archetype:** `FacebookAction`

## Meta Information
- **Title:** Facebook Action
- **Group:** core
- **Type:** action

## Configuration
- **Singleton:** true

## Dependencies
- **Jivas:** `~2.1.0`
- **PulseAction:** `~0.1.0`

---

## How to Use

Below is detailed guidance on how to configure and use the Facebook Action.

### Overview

The Facebook Action provides an abstraction layer for interacting with Facebook via the Facebook Developer API. It supports multiple configurations for various use cases, including:

- **Webhook registration** for message handling.
- **Message broadcasting** to multiple recipients.
- **Integration** with Facebook for sending text, media, location, and posting to facebook page.

### Dynamic Adaptation

The Facebook Action includes advanced mechanisms to optimize message delivery:

- **Automatic Interval Adjustment**: Dynamically modifies send intervals based on success rates to ensure efficient delivery.
- **Variable Batch Sizes**: Alternates batch sizes between defined minimum and maximum values for flexibility.
- **Random Jitter**: Introduces slight randomness to sending intervals to prevent detection of predictable patterns.

These features enhance reliability and minimize disruptions during high-volume messaging operations.
---

### Configuration Structure

To use the Facebook Action, you need to set up the following configuration parameters. These specify connection and behavioral details.

| Parameter                     | Type   | Description                                                                                     | Default                                                                                                                                                             |
| ----------------------------- | ------ | ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `api_url`                     | string | The base URL of the Facebook Graph API.                                                         | `"https://graph.facebook.com/v21.0/"`                                                                                                                             |
| `base_url`                    | string | The base URL of the JIVAS instance.                                                            | `""`                                                                                                                                                                |
| `webhook_url`                 | string | The generated webhook URL.                                                                    | `""`                                                                                                                                                                |
| `app_id`                      | string | The Facebook app ID.                                                                          | `""`                                                                                                                                                                |
| `app_secret`                  | string | The Facebook app secret.                                                                      | `""`                                                                                                                                                                |
| `page_id`                     | string | The Facebook page ID.                                                                         | `""`                                                                                                                                                                |
| `page_access_token`           | string | The Facebook page access token.                                                               | `""`                                                                                                                                                                |
| `webhook_verify_token`        | string | The Facebook webhook verification token.                                                       | `"123"`                                                                                                                                                            |
| `use_pushname`                | bool   | Use the Facebook push name as the user name when set to `True`.                                 | `True`                                                                                                                                                              |
| `chunk_length`                | int    | The maximum length of message to send. Longer texts are split into subsequent messages.        | `1024`                                                                                                                                                              |
| `request_timeout`             | float  | Length of time (in seconds) this action waits for the API to complete a request.              | `10.0`                                                                                                                                                              |
| `outbox_base_rate_per_minute` | int    | The base messages per minute (adapts dynamically).                                              | `20`                                                                                                                                                                |
| `outbox_send_interval`        | float  | The current operational delay between batches.                                                  | `1.0`                                                                                                                                                               |
| `outbox_min_send_interval`    | float  | The absolute minimum delay (seconds).                                                          | `1.0`                                                                                                                                                               |
| `outbox_max_send_interval`    | float  | The maximum allowed delay (seconds).                                                           | `10.0`                                                                                                                                                              |
| `outbox_min_batch_size`       | int    | The minimum batch size of messages to send from the outbox.                                     | `1`                                                                                                                                                                 |
| `outbox_max_batch_size`       | int    | The maximum batch size of messages to send from the outbox.                                     | `10`                                                                                                                                                                |
| `published`                   | bool   | Publish messages to the Facebook page when set to `True`.                                    | `True`                                                                                                                                                                |

---

### Notes on Configuration

- **Parameter Settings**: Ensure all parameters are configured based on your Facebook Server and JIVAS deployment requirements.
- **Webhook URL**: The `webhook_url` must be a publicly accessible endpoint to enable event-driven communication from Facebook.
- **Outbox Base Rate**: Set `outbox_base_rate_per_minute` to `20` for new numbers. This value should align with Facebook's acceptable rate-per-minute limits (default is `20`).
- **Auto Callback**: This when sending or broadcasting messages in batches, this action will trigger your supplied callback upon completion.
- **Batch Size Limits**: For Tier 2 accounts, keep `outbox_max_batch_size` at or below `10` to comply with account limitations.
- **Validation**: Validate your API keys, tokens, and webhook URLs before deploying in production.
- **Chunk Length**: Adjust `chunk_length` if you have use cases that involve very long text messages.
- **Message Filtering**: Use `ignore_newsletters` and `ignore_forwards` to filter out less relevant messages and avoid unnecessary processing.

These guidelines help optimize performance and ensure compliance with Facebook's messaging policies.

---


## API Endpoints

### Broadcast Message

**Endpoint:** `/action/walker`
**Method:** `POST`

#### Parameters

```json
{
   "agent_id": "<AGENT_ID>",
   "walker": "broadcast_message",
   "module_root": "actions.jivas.facebook_action",
   "args": {
      "message": {
         "message_type": "TEXT|MEDIA|MULTI",
         ...
      },
      "ignore_list": ["session_id_1", ...]
   }
}
```

---

### Send Messages

**Endpoint:** `/action/walker`
**Method:** `POST`

#### Parameters

```json
{
   "agent_id": "<AGENT_ID>",
   "walker": "send_messages",
   "module_root": "actions.jivas.facebook_action",
   "args": {
      "messages": [
         // Array of message objects
      ],
      "callback_url": "https://your-callback.url"
   }
}
```

#### Example Request

```json
{
   "messages": [
      {
         "to": "session_id",
         "message": {
            "message_type": "TEXT",
            "content": "Batch message"
         }
      }
   ],
   "callback_url": "https://example.com/status"
}
```

#### Response

Returns a job ID string for tracking.

#### Callback Response

Your callback will receive a JSON payload with the following structure automatically upon job completion:

```json
{
   "status": "success|partial|error",
   "job_id": "<UUID>",
   "processed_count": 10,
   "failed_count": 2,
   "pending_count": 0
}
```

---

### Message Formats

#### TEXT

```json
{
   "message": {
      "message_type": "TEXT",
      "content": "Hello World"
   }
}
```

#### MEDIA

```json
{
   "message": {
      "message_type": "MEDIA",
      "mime": "image/jpeg",
      "content": "Check this!",
      "data": {
         "url": "https://example.com/image.jpg",
         "file_name": "image.jpg"
      }
   }
}
```

#### MULTI

```json
{
   "message": {
      "message_type": "MULTI",
      "content": [
         // Array of TEXT/MEDIA messages
      ]
   }
}
```

---

## Facebook API Guide

### Step 1: Create a New App

1. Go to the [Facebook Developer Console](https://developers.facebook.com/apps/?show_reminder=true).
2. Click **Create a New App**.
3. Enter your **App Name**.
4. Under **Use Cases**, select **Others**.
5. Choose **Business** as the **Account Type**.
6. Click **Create App**.

### Step 2: Retrieve App Secret

1. In the **Sidebar**, navigate to **App Settings > Basic**.
2. Copy the **App Secret**.

### Step 3: Generate Access Token

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/).
2. Under **User or Page**, select the desired **Facebook Page**.
3. Under **Permissions**, select all items under **events**, **groups**, and **pages**.
4. Click **Generate Access Token**.

### Step 4: Extend the Access Token

1. Once the token is generated, click the **Upside-down Exclamation Mark** in the access token field.
2. Open the **Access Token Tool** via the provided button.
3. Scroll to the bottom of the page and click **Extend Access Token**.

### Step 5: Save Required Credentials

Save the following, as you will need them for configuration:
  - **Page ID**
  - **App ID**
  - **Extended Access Token**

---

### Basic Configuration for facebook

```python
base_url = "https://your_base_url"
app_id = "your_app_id"
app_secret = "your_app_secret"
page_id = "your_page_id"
page_access_token = "your_page_access_token"
webhook_verify_token = "your_verify_token"
```



### Best Practices
- Validate your API keys and webhook URLs before deployment.
- Test webhook registration in a staging environment before production use.

---

## 🔰 Contributing

- **🐛 [Report Issues](https://github.com/TrueSelph/facebook_action/issues)**: Submit bugs found or log feature requests for the `facebook_action` project.
- **💡 [Submit Pull Requests](https://github.com/TrueSelph/facebook_action/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your GitHub account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone https://github.com/TrueSelph/facebook_action
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to GitHub**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.
8. **Review**: Once your PR is reviewed and approved, it will be merged into the main branch. Congratulations on your contribution!
</details>

<details open>
<summary>Contributor Graph</summary>
<br>
<p align="left">
    <a href="https://github.com/TrueSelph/facebook_action/graphs/contributors">
        <img src="https://contrib.rocks/image?repo=TrueSelph/facebook_action" />
   </a>
</p>
</details>

## 🎗 License

This project is protected under the Apache License 2.0. See [LICENSE](./LICENSE) for more information.