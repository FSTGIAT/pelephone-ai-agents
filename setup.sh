#!/bin/bash
# Pelephone AI Agent System Setup Script for Linux/Unix
# This script initializes the project structure and sets up Docker containers

echo "Pelephone AI Agent System - Setup Script"
echo "-------------------------------------"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed."
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed."
    echo "Please install Docker Compose first: https://docs.docker.com/compose/install/"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Created .env file - Please update with secure passwords"
else
    echo ".env file already exists, skipping..."
fi

# Create required directories if they don't exist
echo "Creating project directory structure..."
mkdir -p agents/billing agents/international agents/supervisor
mkdir -p api
mkdir -p frontend/src/assets frontend/src/components frontend/src/views
mkdir -p database/migrations
mkdir -p orchestration/workflows orchestration/state
mkdir -p security/auth security/encryption
mkdir -p docs

echo "Directory structure created"

# Create placeholder for assets
touch frontend/src/assets/.gitkeep

# Build and start the containers
echo "Starting Docker containers..."
docker-compose build
docker-compose up -d

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
RETRIES=30
until docker-compose exec -T postgres pg_isready -U pelephone || [ $RETRIES -eq 0 ]; do
    echo "Waiting for PostgreSQL server, $RETRIES remaining attempts..."
    RETRIES=$((RETRIES-1))
    sleep 2
done

if [ $RETRIES -eq 0 ]; then
    echo "PostgreSQL did not become ready in time"
else
    # Run database migrations
    echo "Running database migrations..."
    if ! docker-compose exec -T api alembic upgrade head; then
        echo "Failed to run migrations"
    fi
fi

# Print information about the running services
echo
echo "Setup completed!"
echo "Services:"
echo "- Frontend: http://localhost"
echo "- API: http://localhost:8000"
echo "- API Documentation: http://localhost:8000/docs"
echo "- Kibana (Logs): http://localhost:5601"
echo "- RabbitMQ Management: http://localhost:15672"
echo "- Keycloak (SSO): http://localhost:8080"

echo
echo "Default credentials are in your .env file"
echo "For production use, further configuration is required"

echo
echo "Next steps:"
echo "1. Configure Keycloak for authentication"
echo "2. Customize the AI models for your specific use case"
echo "3. Set up proper monitoring and alerting"

echo
echo "Thank you for using Pelephone AI Agent System!"