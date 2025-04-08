# Pelephone AI Agent System

A comprehensive system of specialized AI agents for handling customer service inquiries at Pelephone:

- **Billing Agent**: Resolves billing issues and discrepancies
- **International Calls Agent**: Handles international usage and roaming problems
- **Supervisor Agent**: Coordinates tasks and handles escalations

## Project Overview

This system implements a multi-agent AI architecture for Pelephone's customer service. It uses specialized AI models for different domains of customer inquiries and provides a unified experience through a modern Vue.js frontend.

### Key Features

- **Specialized AI Agents**: Domain-specific models for billing and international call inquiries
- **Orchestration**: Coordinated workflows between agents handled by a supervisor agent
- **State Management**: Redis and RabbitMQ for reliable session and message handling
- **Security**: JWT authentication and SSL/TLS encryption for APIs
- **Monitoring**: ELK Stack for logs and metrics visualization
- **Deployment**: Docker and Docker Compose for easy setup

## Project Structure

```
pelephone-ai-agent-system/
├── agents/                  # AI agent implementations
│   ├── billing/             # Billing agent
│   ├── international/       # International calls agent
│   └── supervisor/          # Supervisor agent
├── api/                     # FastAPI backend service
├── database/                # Database schemas and migrations
├── frontend/                # Vue.js frontend application
├── orchestration/           # Workflow and state management
├── security/                # Authentication and data protection
├── docs/                    # Project documentation
├── docker-compose.yml       # Docker Compose configuration
└── .env.example             # Environment variables template
```

## Tech Stack

- **AI Models**: Fine-tuned Hugging Face models (T5, BERT, DistilBERT)
- **Orchestration**: Mistral for workflow automation
- **State Management**: Redis for caching, RabbitMQ for messaging
- **Database**: PostgreSQL (designed for Oracle compatibility)
- **API**: FastAPI with JWT authentication
- **Frontend**: Vue.js 3 with Element Plus UI components
- **Monitoring**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Authentication**: Keycloak for SSO
- **Deployment**: Docker and Docker Compose

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git
- Node.js (for local frontend development)
- Python 3.10+ (for local backend development)

### Initial Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/pelephone-ai-agent-system.git
   cd pelephone-ai-agent-system
   ```

2. Create environment file:
   ```bash
   cp .env.example .env
   ```
   
3. Update the `.env` file with your specific configuration values.

4. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

5. Initialize the database:
   ```bash
   docker-compose exec api alembic upgrade head
   ```

6. Access the application:
   - Frontend: http://localhost
   - API: http://localhost:8000
   - Kibana: http://localhost:5601
   - Keycloak: http://localhost:8080

### Development Workflow

For frontend development:
```bash
cd frontend
npm install
npm run serve
```

For backend development:
```bash
cd api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## API Documentation

Once the application is running, you can access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

These provide interactive documentation of all available API endpoints.

## Agent Capabilities

### Billing Agent

The Billing Agent can handle the following types of inquiries:

- **Billing Inquiries**: General questions about bills, payment methods, or charges
- **Usage Discrepancies**: Analyze and resolve differences between reported and billed usage
- **Refund Requests**: Process refunds for valid customer claims
- **Plan Changes**: Update customer plans and handle associated billing adjustments

### International Calls Agent

The International Calls Agent specializes in:

- **International Usage Inquiries**: Questions about international call rates and data usage
- **Roaming Issues**: Activation, deactivation, and troubleshooting of roaming services
- **International Package Management**: Subscription to international calling and data packages
- **Billing Discrepancies**: Resolution of issues specifically related to international charges

### Supervisor Agent

The Supervisor Agent serves as a coordinator and overseer:

- **Task Coordination**: Route requests to the appropriate specialized agent
- **Escalation Handling**: Process requests that require higher authorization levels
- **Metrics Tracking**: Monitor performance and efficiency of the agent system
- **Log Management**: Track and analyze system behavior and customer interactions

## Deployment Options

### Standard Deployment

```bash
docker-compose up -d
```

This will start all services defined in the docker-compose.yml file.

### Partial Deployment

You can deploy specific components:

```bash
# Backend services only
docker-compose up -d postgres redis rabbitmq api

# Frontend only
docker-compose up -d frontend
```

### Production Deployment

For production environments, use the production configuration:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Monitoring and Logs

All system logs are collected and can be viewed through Kibana:

1. Access Kibana at http://localhost:5601
2. Navigate to "Discover" to view logs
3. Use the pre-configured dashboards to view system metrics

## Security Configuration

### Keycloak Setup

1. Access Keycloak admin console at http://localhost:8080
2. Login with admin credentials from your .env file
3. Create a new realm "pelephone"
4. Create client for the API and frontend
5. Set up roles and users

### API Security

The API uses JWT tokens for authentication. To make authenticated requests:

1. Obtain a token from `/token` endpoint
2. Include the token in the Authorization header: `Bearer <token>`

## Performance Tuning

### Redis Configuration

Edit the Redis configuration in docker-compose.yml to adjust memory allocation and persistence options.

### PostgreSQL Tuning

For large deployments, consider adjusting PostgreSQL settings:

```yaml
postgres:
  command: >
    postgres
    -c max_connections=200
    -c shared_buffers=2GB
    -c effective_cache_size=6GB
```

## Testing

### Running Tests

```bash
# API tests
docker-compose exec api pytest

# Agent tests
docker-compose exec billing-agent pytest
docker-compose exec international-agent pytest
docker-compose exec supervisor-agent pytest
```

### Load Testing

A load testing script is provided to simulate multiple concurrent users:

```bash
cd tests
python load_test.py --concurrency 50 --duration 60
```

## Troubleshooting

### Common Issues

1. **Container startup failures**:
   - Check logs with `docker-compose logs <service_name>`
   - Ensure all required environment variables are set

2. **Database connection issues**:
   - Verify PostgreSQL is running: `docker-compose ps postgres`
   - Check database credentials in .env file

3. **Message queue problems**:
   - Inspect RabbitMQ management console at http://localhost:15672
   - Ensure queues are properly declared

### Resetting the System

To completely reset the system:

```bash
docker-compose down -v
docker-compose up -d
docker-compose exec api alembic upgrade head
```

## Contributing

Please refer to [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines on contributing to this project.

## License

This project is proprietary and confidential.

## Contact

For questions or support, please contact your project administrator.