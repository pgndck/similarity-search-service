# Similarity Search Service

This project is a gRPC-based similarity search service implemented in Python, which is containerized using Docker for easy deployment and scalability. It uses a PostgreSQL database to store items and search results.

## Prerequisites

-   Docker
-   Docker-compose
-   Python 3.8+
-   A running PostgreSQL database

## Building and Running the Dockerized Application

1. **Clone the repository:**

```bash
git clone https://github.com/pgndck/similarity-search-service.git
cd similarity-search-service
```

2. **Build the Docker image:**

```bash
docker-compose build
```

3. **Run the Docker container:**

```bash
docker-compose up
```

Your application should now be running and accessible on port 5001.

4. _But as I didn't manage to do this in time, I couldn't finish setting up docker image in time :/ That is why you should just run:_

```bash
python ./server.py
```

## Usage

You can interact with the service using a gRPC client. The service provides three gRPC methods:

-   AddItem: Adds a new item to the database.
-   SearchItems: Performs a similarity search in the database.
-   GetSearchResults: Retrieves the search results from the database.

## Running the Tests

To run the unit tests inside the Docker container, use:

```bash
docker-compose run similarity-service python -m unittest
```

## Database Connection

Update the PostgreSQL connection parameters in the .env to match your running PostgreSQL server.
