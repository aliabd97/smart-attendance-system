"""
RabbitMQ Client for message queue communication
Used by all services for asynchronous operations
"""

import pika
import json
import os
from typing import Callable, Dict

# Queue definitions
QUEUES = {
    'pdf_processing': {
        'durable': True,
        'auto_delete': False,
        'arguments': {
            'x-message-ttl': 3600000,  # 1 hour
            'x-max-length': 1000
        }
    },
    'attendance_recording': {
        'durable': True,
        'auto_delete': False
    },
    'report_generation': {
        'durable': True,
        'auto_delete': False
    },
    'notifications': {
        'durable': True,
        'auto_delete': False
    }
}


class RabbitMQClient:
    """
    RabbitMQ client for publishing and consuming messages
    Handles connection management and queue setup
    """

    def __init__(self, host: str = None):
        """
        Initialize RabbitMQ connection

        Args:
            host: RabbitMQ server host (defaults to RABBITMQ_HOST env var or localhost)
        """
        self.host = host or os.getenv('RABBITMQ_HOST', 'localhost')
        self.connection = None
        self.channel = None
        self._connect()

    def _connect(self):
        """Establish connection to RabbitMQ server"""
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.host)
            )
            self.channel = self.connection.channel()
            self._setup_queues()
            print(f"✅ Connected to RabbitMQ at {self.host}")
        except Exception as e:
            print(f"❌ Failed to connect to RabbitMQ: {e}")
            raise

    def _setup_queues(self):
        """Declare all queues with their configurations"""
        for queue_name, config in QUEUES.items():
            self.channel.queue_declare(
                queue=queue_name,
                **config
            )
            print(f"✅ Queue '{queue_name}' declared")

    def publish(self, queue_name: str, message: dict):
        """
        Publish a message to a queue

        Args:
            queue_name: Name of the queue
            message: Dictionary to send (will be JSON encoded)
        """
        try:
            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json'
                )
            )
            print(f"📤 Published message to queue '{queue_name}'")
        except Exception as e:
            print(f"❌ Failed to publish message: {e}")
            raise

    def consume(self, queue_name: str, callback: Callable):
        """
        Start consuming messages from a queue

        Args:
            queue_name: Name of the queue to consume from
            callback: Function to call for each message
        """
        try:
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback,
                auto_ack=False
            )
            print(f"📥 Started consuming from queue '{queue_name}'")
            self.channel.start_consuming()
        except Exception as e:
            print(f"❌ Failed to consume messages: {e}")
            raise

    def close(self):
        """Close RabbitMQ connection"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            print("✅ RabbitMQ connection closed")
