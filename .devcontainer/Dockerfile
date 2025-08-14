# Force Ubuntu so apt & Heroku installer work
FROM mcr.microsoft.com/devcontainers/base:ubuntu

# Ensure 'vscode' user exists (belt & braces)
RUN if ! id -u vscode >/dev/null 2>&1; then \
      useradd -m -s /bin/bash vscode && \
      echo "vscode ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers; \
    fi

# Tools: Node 20.x (binary), Python, Postgres client, Heroku CLI
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
      curl gnupg lsb-release ca-certificates \
      build-essential git unzip \
      python3 python3-pip python3-venv \
      postgresql-client \
      software-properties-common \
  && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
  && apt-get install -y nodejs \
  && curl https://cli-assets.heroku.com/install-ubuntu.sh | sh \
  && npm install -g npm@latest \
  && rm -rf /var/lib/apt/lists/*

USER vscode
ENV HOME=/home/vscode
WORKDIR /workspaces/autorisen
