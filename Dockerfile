# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed for Chrome
RUN apt-get update -qq && apt-get install -y \
    wget curl unzip gnupg ca-certificates jq \
    fonts-liberation libasound2 libatk-bridge2.0-0 libatk1.0-0 \
    libcups2 libdrm2 libgbm1 libxcomposite1 libxdamage1 libxrandr2 \
    xdg-utils libu2f-udev libvulkan1 libnss3 libxshmfence1 \
    libwayland-client0 libwayland-cursor0 libxkbcommon0 \
    libpangocairo-1.0-0 libpango-1.0-0 libgtk-3-0 \
    libatspi2.0-0 libdbus-1-3 libexpat1 libfontconfig1 \
    libfreetype6 libharfbuzz0b libjpeg62-turbo libpng16-16 \
    libx11-6 libx11-xcb1 libxcb1 libxcursor1 libxext6 libxfixes3 \
    libxi6 libxinerama1 libxrender1 libxss1 libxtst6 lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Download and install the latest stable Chrome and Chromedriver
RUN set -eux; \
    # Get download URLs
    curl -sS https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json \
        -o /tmp/versions.json; \
    CHROME_URL=$(jq -r '.channels.Stable.downloads.chrome[] | select(.platform=="linux64") | .url' /tmp/versions.json); \
    CHROMEDRIVER_URL=$(jq -r '.channels.Stable.downloads.chromedriver[] | select(.platform=="linux64") | .url' /tmp/versions.json); \
    # Install Chrome
    wget -q "$CHROME_URL" -O /tmp/chrome.zip; \
    unzip /tmp/chrome.zip -d /opt/; \
    rm /tmp/chrome.zip; \
    # Find the Chrome binary dynamically and move it to the PATH
    CHROME_BIN=$(find /opt -type f -name 'chrome' | head -n 1); \
    mv "$CHROME_BIN" /usr/local/bin/google-chrome; \
    chmod +x /usr/local/bin/google-chrome; \
    # Install Chromedriver
    wget -q "$CHROMEDRIVER_URL" -O /tmp/chromedriver.zip; \
    unzip /tmp/chromedriver.zip -d /opt/; \
    mv /opt/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver; \
    # Clean up
    rm -rf /opt/chromedriver-linux64 /tmp/chromedriver.zip /tmp/versions.json; \
    chmod +x /usr/local/bin/chromedriver

# Copy only requirements first (for better caching)
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy rest of the project files
COPY . .

# Define the default command
CMD ["python", "led_scraping.py"]