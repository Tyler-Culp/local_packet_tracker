FROM python:3.10

# Set the working directory within the container
WORKDIR /usr/local/app

# Copy the necessary files and directories into the container
COPY analyzeAPI/flaskServer/ /usr/local/app

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install git+https://github.com/julian-r/python-magic.git

# Expose port 5432 for the Flask application
EXPOSE 5432

RUN useradd app
USER app

# Define the command to run the Flask application
CMD ["python3", "app.py"]