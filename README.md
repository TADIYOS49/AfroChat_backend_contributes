# AfroChat Backend

Welcome to the AfroChat Backend repository! This README provides essential information on setting up and running the
backend server for AfroChat. Follow these steps to get started with your development environment.

## Table of Contents

- [AfroChat Backend](#afrochat-backend)
    - [Table of Contents](#table-of-contents)
    - [Getting Started](#getting-started)
        - [First Migration](#first-migration)
        - [First-Time Build](#first-time-build)
        - [Running the App](#running-the-app)
    - [Installation](#installation)

## Getting Started

### First Migration

To initialize your database migrations using Alembic, use the following commands:

```bash
alembic init -t async migrations
```

To generate a migration commit after performing operations on the database model:

```bash
alembic revision --autogenerate -m "alembic commit"
```

To apply the changes:

```bash
alembic upgrade heads
```

### First-Time Build

For the first-time build of the Docker container:

```bash
docker build -t afro-chat-backend -f Dockerfile.dev .
```

```bash
docker run -v "$(pwd):/app" -p 8000:8000 --memory=512m --cpus="1" --name=afro-chat-backend afro-chat-backend
```

### Running the App

To run the app next time

```bash
docker start afro-chat-backend -i
```

## Installation

To get started with this repository, follow these steps:

1. Clone the repository:

```bash
git clone <repository-url>
cd afro-chat-backend
```

2. Create an `.env` file with the necessary environment variables.

3. Build the Docker image (only for the first-time setup):

```bash
docker build -t afro-chat-backend -f Dockerfile.dev .
```

4. Run the Docker container (use only if running for the first time):

```bash
docker run -v "$(pwd):/app" -p 8000:8000 --memory=512m --cpus="1" --name=afro-chat-backend afro-chat-backend
```

5. Enter the container using bash mode:

```bash
docker exec -it afro-chat-backend bash
```

6. Apply all the database schema changes:

```bash
alembic upgrade heads
```

7. Exit from the container.

To start the container in the future, use:

```bash
docker start afro-chat-backend -i
```

# using docker compose

1. build the containers

```bash
docker-compose build
```

2. start the containers

```bash
docker-compose up -d 
```

3. to track the logs

```bash
docker logs afro-chat-backend --follow
```

4. to stop the containers

```bash
docker-compose down -v
```

# Perfom Test

1. Create a testdb if it doesn't exists

```bash
docker-compose exec db createdb -U root testdb
```

2. Run the test

```bash
docker-compose exec backend pytest -s .
```

# Run black formatter before pushing

```bash
docker-compose exec backend black .
```
