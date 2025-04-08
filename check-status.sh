#!/bin/bash

echo "Checking Pelephone AI Agent System services..."
echo

# Check Docker services
echo "=== Docker Container Status ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo

# Check specific services
echo "=== Service Health Checks ==="

# Check PostgreSQL
echo -n "PostgreSQL: "
if docker exec pelephone-postgres pg_isready -U pelephone > /dev/null 2>&1; then
    echo "Running"
else
    echo "Not responding"
fi

# Check Redis
echo -n "Redis: "
if docker exec pelephone-redis redis-cli ping > /dev/null 2>&1; then
    echo "Running"
else
    echo "Not responding"
fi

# Check API
echo -n "API: "
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "Running"
else
    echo "Not responding"
fi

# Check Frontend
echo -n "Frontend: "
if curl -s http://localhost/ > /dev/null 2>&1; then
    echo "Running"
else
    echo "Not responding"
fi

echo
echo "=== Next Steps ==="
echo "1. Access the frontend at: http://localhost"
echo "2. Access the API docs at: http://localhost:8000/docs (if API is running)"
echo "3. Check container logs with: docker logs <container-name>"