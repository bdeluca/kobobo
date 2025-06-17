# Use a lightweight Python base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file
COPY ../requirements.txt .
COPY ../src/ .
COPY docker/docker-entrypoint.sh /usr/local/bin/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

ENV KOBOBO_CALIBRE_URL=http://127.0.0.1
ENV KOBOBO_USERNAME=password
ENV KOBOBO_PASSWORD=password




EXPOSE 5003

# Set the entry point or default command to run your Flask app
# The command below assumes your Flask app’s entry point is in app.py
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["python", "app.py"]


