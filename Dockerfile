FROM python:3.8

# Set the working directory in the container to /app
WORKDIR /app

# Add current directory contents to the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the database wait script
COPY db_sync.py .

# Make port 5001 available to the world outside this container
EXPOSE 5001

# Run wait_for_db.py to ensure the database is ready, then run server.py when the container launches
CMD ["sh", "-c", "python db_sync.py && python server.py"]