"""
Service Registry
Port: 5008
Service discovery and health monitoring
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import threading
import time

app = Flask(__name__)
CORS(app)

# In-memory service registry
SERVICES = {}
HEALTH_CHECK_INTERVAL = 30  # seconds


class ServiceRegistry:
    """Manages service registration and discovery"""

    @staticmethod
    def register(service_name: str, host: str, port: int, metadata: dict = None):
        """
        Register a service

        Args:
            service_name: Name of the service
            host: Host address
            port: Port number
            metadata: Additional metadata
        """
        SERVICES[service_name] = {
            'host': host,
            'port': port,
            'url': f'http://{host}:{port}',
            'last_heartbeat': datetime.now(),
            'status': 'healthy',
            'registered_at': datetime.now(),
            'metadata': metadata or {}
        }
        print(f"✅ Service registered: {service_name} at {host}:{port}")

    @staticmethod
    def deregister(service_name: str):
        """Remove service from registry"""
        if service_name in SERVICES:
            del SERVICES[service_name]
            print(f"❌ Service deregistered: {service_name}")
            return True
        return False

    @staticmethod
    def get_service(service_name: str) -> dict:
        """
        Get service information

        Args:
            service_name: Name of the service

        Returns:
            Service information or None
        """
        service = SERVICES.get(service_name)
        if not service:
            return None

        # Check if service is healthy (recent heartbeat)
        time_since_heartbeat = datetime.now() - service['last_heartbeat']
        if time_since_heartbeat > timedelta(seconds=HEALTH_CHECK_INTERVAL * 2):
            service['status'] = 'unhealthy'
            return None

        return service

    @staticmethod
    def heartbeat(service_name: str):
        """Update service heartbeat"""
        if service_name in SERVICES:
            SERVICES[service_name]['last_heartbeat'] = datetime.now()
            SERVICES[service_name]['status'] = 'healthy'
            return True
        return False

    @staticmethod
    def get_all_services() -> dict:
        """Get all registered services"""
        # Update status based on heartbeat
        for service_name, service in SERVICES.items():
            time_since_heartbeat = datetime.now() - service['last_heartbeat']
            if time_since_heartbeat > timedelta(seconds=HEALTH_CHECK_INTERVAL * 2):
                service['status'] = 'unhealthy'
            else:
                service['status'] = 'healthy'

        return SERVICES

    @staticmethod
    def get_healthy_services() -> dict:
        """Get only healthy services"""
        all_services = ServiceRegistry.get_all_services()
        return {k: v for k, v in all_services.items() if v['status'] == 'healthy'}


@app.route('/')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'service': 'Service Registry',
        'status': 'healthy',
        'port': 5008,
        'version': '1.0.0',
        'registered_services': len(SERVICES)
    }), 200


@app.route('/api/register', methods=['POST'])
def register():
    """
    Register a service

    Request:
    {
        "name": "student-service",
        "host": "localhost",
        "port": 5001,
        "metadata": {
            "version": "1.0.0",
            "description": "Student Management"
        }
    }
    """
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('name') or not data.get('host') or not data.get('port'):
            return jsonify({'error': 'Name, host, and port required'}), 400

        ServiceRegistry.register(
            service_name=data['name'],
            host=data['host'],
            port=data['port'],
            metadata=data.get('metadata')
        )

        return jsonify({
            'message': 'Service registered successfully',
            'service_name': data['name']
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/deregister/<service_name>', methods=['DELETE'])
def deregister(service_name):
    """Deregister a service"""
    try:
        if ServiceRegistry.deregister(service_name):
            return jsonify({
                'message': 'Service deregistered successfully',
                'service_name': service_name
            }), 200
        else:
            return jsonify({'error': 'Service not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/discover/<service_name>', methods=['GET'])
def discover(service_name):
    """
    Discover a service by name

    Response:
    {
        "url": "http://localhost:5001",
        "host": "localhost",
        "port": 5001,
        "status": "healthy"
    }
    """
    try:
        service = ServiceRegistry.get_service(service_name)

        if not service:
            return jsonify({'error': 'Service not found or unhealthy'}), 404

        return jsonify({
            'service_name': service_name,
            'url': service['url'],
            'host': service['host'],
            'port': service['port'],
            'status': service['status'],
            'metadata': service.get('metadata', {})
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/heartbeat/<service_name>', methods=['POST'])
def heartbeat(service_name):
    """
    Receive heartbeat from a service
    Services should send heartbeat every 30 seconds
    """
    try:
        if ServiceRegistry.heartbeat(service_name):
            return jsonify({'message': 'Heartbeat received'}), 200
        else:
            return jsonify({'error': 'Service not registered'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/services', methods=['GET'])
def list_services():
    """List all registered services"""
    try:
        services = ServiceRegistry.get_all_services()

        # Format response
        services_list = []
        for name, info in services.items():
            services_list.append({
                'name': name,
                'url': info['url'],
                'host': info['host'],
                'port': info['port'],
                'status': info['status'],
                'last_heartbeat': info['last_heartbeat'].isoformat(),
                'registered_at': info['registered_at'].isoformat(),
                'metadata': info.get('metadata', {})
            })

        return jsonify({
            'count': len(services_list),
            'services': services_list
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/services/healthy', methods=['GET'])
def list_healthy_services():
    """List only healthy services"""
    try:
        services = ServiceRegistry.get_healthy_services()

        services_list = []
        for name, info in services.items():
            services_list.append({
                'name': name,
                'url': info['url'],
                'status': info['status']
            })

        return jsonify({
            'count': len(services_list),
            'services': services_list
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def auto_register_services():
    """Auto-register known services on startup"""
    default_services = [
        {'name': 'student-service', 'host': 'localhost', 'port': 5001},
        {'name': 'course-service', 'host': 'localhost', 'port': 5002},
        {'name': 'bubble-sheet-service', 'host': 'localhost', 'port': 5003},
        {'name': 'pdf-processing-service', 'host': 'localhost', 'port': 5004},
        {'name': 'attendance-service', 'host': 'localhost', 'port': 5005},
        {'name': 'reporting-service', 'host': 'localhost', 'port': 5006},
        {'name': 'auth-service', 'host': 'localhost', 'port': 5007},
        {'name': 'api-gateway', 'host': 'localhost', 'port': 5000},
    ]

    print("\n🔄 Auto-registering services...")
    for service in default_services:
        ServiceRegistry.register(
            service_name=service['name'],
            host=service['host'],
            port=service['port']
        )


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("📋 Service Registry")
    print("=" * 60)
    print("Port: 5008")
    print("Features: Service Discovery, Health Monitoring")
    print("=" * 60)

    # Auto-register default services
    auto_register_services()

    print("\n✅ Service Registry is running")
    print("=" * 60)

    app.run(host='0.0.0.0', port=5008, debug=True)
