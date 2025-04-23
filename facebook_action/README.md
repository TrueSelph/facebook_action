# Facebook Action

![GitHub release (latest by date)](https://img.shields.io/github/v/release/TrueSelph/facebook_action)
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/TrueSelph/facebook_action/test-facebook_action.yaml)
![GitHub issues](https://img.shields.io/github/issues/TrueSelph/facebook_action)
![GitHub pull requests](https://img.shields.io/github/issues-pr/TrueSelph/facebook_action)
![GitHub](https://img.shields.io/github/license/TrueSelph/facebook_action)

This action manages agent configurations for communication through the Facebook API, ensuring robust, secure, and efficient interactions with Facebook’s platform. As a singleton in the action group, it provides centralized management for Facebook integrations. This package requires the Jivas library version 2.0.0 and above.

## Package Information

- **Name:** `jivas/facebook_action`
- **Author:** [V75 Inc.](https://v75inc.com/)
- **Architype:** `FacebookAction`
- **Version:** 0.0.1

## Meta Information

- **Title:** Facebook Action
- **Description:** Manages configurations per agent for Facebook API communications.
- **Group:** core
- **Type:** action

## Configuration
- **Singleton:** true

## Dependencies
- **Jivas:** ^2.0.0

---

### Best Practices
- Always store your Facebook App secrets and access tokens securely.
- Regularly update and rotate access tokens to maintain security.
- Test configurations in a staging environment before going live.

---

## 🚀 Facebook API Setup Guide

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

## 🔰 Contributing

- **🐛 [Report Issues](https://github.com/TrueSelph/facebook_action/issues)**: Found a bug or want to request a feature? Submit it here.
- **💡 [Submit Pull Requests](https://github.com/TrueSelph/facebook_action/blob/main/CONTRIBUTING.md)**: Check out open PRs or submit your own improvements.

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

This project is protected under the Apache License 2.0. See [LICENSE](../LICENSE) for more information.