@echo off
REM Pelephone AI Agent System Setup Script for Windows
REM This script initializes the project structure and sets up Docker containers

echo Pelephone AI Agent System - Setup Script
echo -------------------------------------

REM Check if Docker is installed
docker --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker is not installed.
    echo Please install Docker first: https://docs.docker.com/get-docker/
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker Compose is not installed.
    echo Please install Docker Compose first: https://docs.docker.com/compose/install/
    exit /b 1
)

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo Created .env file - Please update with secure passwords
) else (
    echo .env file already exists, skipping...
)

REM Create required directories if they don't exist
echo Creating project directory structure...
if not exist agents mkdir agents
if not exist agents\billing mkdir agents\billing
if not exist agents\international mkdir agents\international
if not exist agents\supervisor mkdir agents\supervisor
if not exist api mkdir api
if not exist frontend mkdir frontend
if not exist frontend\src mkdir frontend\src
if not exist frontend\src\assets mkdir frontend\src\assets
if not exist frontend\src\components mkdir frontend\src\components
if not exist frontend\src\views mkdir frontend\src\views
if not exist database mkdir database
if not exist database\migrations mkdir database\migrations
if not exist orchestration mkdir orchestration
if not exist orchestration\workflows mkdir orchestration\workflows
if not exist orchestration\state mkdir orchestration\state
if not exist security mkdir security
if not exist security\auth mkdir security\auth
if not exist security\encryption mkdir security\encryption
if not exist docs mkdir docs

echo Directory structure created

REM Create placeholder for assets
if not exist frontend\src\assets\.gitkeep type nul > frontend\src\assets\.gitkeep

REM Build and start the containers
echo Starting Docker containers...
docker-compose build
docker-compose up -d

REM Wait for PostgreSQL to be ready
echo Waiting for PostgreSQL to be ready...
set RETRIES=30
:WAIT_FOR_POSTGRES
if %RETRIES% equ 0 goto POSTGRES_FAILED
docker-compose exec -T postgres pg_isready -U pelephone > nul 2>&1
if %errorlevel% equ 0 goto POSTGRES_READY
set /a RETRIES=%RETRIES%-1
echo Waiting for PostgreSQL server, %RETRIES% remaining attempts...
timeout /t 2 > nul
goto WAIT_FOR_POSTGRES

:POSTGRES_FAILED
echo PostgreSQL did not become ready in time
goto FINALIZE

:POSTGRES_READY
REM Run database migrations
echo Running database migrations...
docker-compose exec -T api alembic upgrade head
if %errorlevel% neq 0 echo Failed to run migrations

:FINALIZE
REM Print information about the running services
echo.
echo Setup completed!
echo Services:
echo - Frontend: http://localhost
echo - API: http://localhost:8000
echo - API Documentation: http://localhost:8000/docs
echo - Kibana (Logs): http://localhost:5601
echo - RabbitMQ Management: http://localhost:15672
echo - Keycloak (SSO): http://localhost:8080

echo.
echo Default credentials are in your .env file
echo For production use, further configuration is required

echo.
echo Next steps:
echo 1. Configure Keycloak for authentication
echo 2. Customize the AI models for your specific use case
echo 3. Set up proper monitoring and alerting

echo.
echo Thank you for using Pelephone AI Agent System!