# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy files
COPY . /app

# Install OS dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    ca-certificates \
    xvfb \
    fonts-liberation \
    xdg-utils \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-linux.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
    > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Install matching ChromeDriver
RUN set -eux; \
    CHROME_BIN=$(command -v google-chrome-stable); \
    echo "Chrome binary: $CHROME_BIN"; \
    CHROME_VERSION=$($CHROME_BIN --version | sed 's/Google Chrome //'); \
    echo "Installed Chrome version: $CHROME_VERSION"; \
    CHROME_MAJOR_VERSION=$(echo $CHROME_VERSION | cut -d. -f1); \
    echo "Chrome major version: $CHROME_MAJOR_VERSION"; \
    DRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_MAJOR_VERSION}"); \
    echo "Matching ChromeDriver version: $DRIVER_VERSION"; \
    wget -q -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${DRIVER_VERSION}/chromedriver_linux64.zip"; \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/; \
    chmod +x /usr/local/bin/chromedriver; \
    rm /tmp/chromedriver.zip

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Define the default command
CMD ["python", "led_scraping.py"]