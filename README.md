# MTProto Proxy Web UI Manager

A simple, secure, and powerful web-based UI to install and manage multiple types of MTProto proxy servers on your Linux machine. This panel acts as a graphical frontend for the powerful command-line scripts originally developed by Hirbod Behnam, allowing you to manage your proxies without ever touching the terminal after the initial setup.



## Features

-   **Graphical Management:** A clean web interface to control your proxy services.
-   **One-Line Installer:** Get the web UI up and running with a single command.
-   **Secure Access:** The panel is protected by a randomly generated password for security.
-   **Multi-Proxy Support:** Manage different proxy implementations from one place:
    -   Official C Proxy (`MTProtoProxyOfficialInstall.sh`)
    -   Python Proxy (`MTProtoProxyInstall.sh`)
    -   Golang (MTG) Proxy (`MTGInstall.sh`)
-   **Service Status Overview:** Quickly check if your proxy services are active, inactive, or not installed.
-   **Direct Command Execution:** Run the underlying scripts with custom arguments directly from the UI and see the real-time output.

---

## Requirements

Before you begin, ensure your server meets the following requirements:

-   **Operating System:** A modern Linux distribution such as:
    -   Ubuntu 18.04 or later
    -   Debian 10 or later
    -   CentOS 7 or later
-   **Permissions:** You must have **root** access (`sudo`).
-   **Software:** `git` and `curl` must be installed. They are usually pre-installed, but if not, you can install them with your package manager (e.g., `sudo apt install git curl`).

---

## Quick Installation

To install the MTProto Proxy Web UI, simply run the following command on your server as the root user:

```bash
git clone [https://github.com/Hamedgunner/MTProtoUI.git](https://github.com/Hamedgunner/MTProtoUI.git) && cd MTProtoUI && chmod +x install_webui.sh && sudo ./install_webui.sh
