# Django Docker Project

This project is a Django application configured to run within a Docker container. It provides a simple setup for developing and deploying Django applications using Docker.

## Project Structure

```
django-docker-project
├── app
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
└── README.md
```

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Installation

1. Clone the repository:

   ```
   git clone <repository-url>
   cd django-docker-project
   ```

2. Build the Docker image:

   ```
   docker-compose build
   ```

3. Run the application:

   ```
   docker-compose up
   ```

### Usage

Once the application is running, you can access it at `http://localhost:8000`.

### Running Migrations

To apply database migrations, you can run:

```
docker-compose run app python manage.py migrate
```

### Stopping the Application

To stop the application, use:

```
docker-compose down
```

## Contributing

Feel free to submit issues or pull requests for improvements or bug fixes.

## License

This project is licensed under the MIT License.