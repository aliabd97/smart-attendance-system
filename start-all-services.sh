#!/bin/bash

echo "========================================"
echo "Smart Attendance Management System"
echo "Starting All Services"
echo "========================================"
echo ""

echo "Starting RabbitMQ (Docker)..."
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 \
  -e RABBITMQ_DEFAULT_USER=admin \
  -e RABBITMQ_DEFAULT_PASS=admin123 \
  rabbitmq:3-management
sleep 10

echo ""
echo "Starting Service Registry (Port 5008)..."
cd service-registry && python app.py &
sleep 3

echo ""
echo "Starting Auth Service (Port 5007)..."
cd ../auth-service && python app.py &
sleep 3

echo ""
echo "Starting Student Service (Port 5001)..."
cd ../student-service && python app.py &
sleep 3

echo ""
echo "Starting Course Service (Port 5002)..."
cd ../course-service && python app.py &
sleep 3

echo ""
echo "Starting Attendance Service (Port 5005)..."
cd ../attendance-service && python app.py &
sleep 3

echo ""
echo "Starting API Gateway (Port 5000)..."
cd ../api-gateway && python app.py &
sleep 3

echo ""
echo "========================================"
echo "All Services Started!"
echo "========================================"
echo ""
echo "Service URLs:"
echo "  API Gateway:        http://localhost:5000"
echo "  Student Service:    http://localhost:5001"
echo "  Course Service:     http://localhost:5002"
echo "  Attendance Service: http://localhost:5005"
echo "  Auth Service:       http://localhost:5007"
echo "  Service Registry:   http://localhost:5008"
echo "  RabbitMQ UI:        http://localhost:15672 (admin/admin123)"
echo ""
echo "Default Login:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo "========================================"
