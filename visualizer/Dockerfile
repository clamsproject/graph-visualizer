# Use the latest Python 3.9 image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Clone the repository
RUN apt-get update && apt-get install -y git
RUN git clone https://github.com/clamsproject/mmif-visualizer.git .

# Install the requirements
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]