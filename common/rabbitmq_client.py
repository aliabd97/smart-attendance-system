"""
RabbitMQ Client - Message Broker for Choreography Pattern

This implements the Choreography pattern:
- Services communicate through events (messages) via RabbitMQ
- No central coordinator - each service reacts independently to events
- Loose coupling between services

Queue: attendance_events
- Producer: Attendance Service (publishes after recording attendance)
- Consumer: Course Service (reads events and updates attendance stats)
"""

import pika
import json
import os
from typing import Callable


class RabbitMQClient:
    """Simple RabbitMQ client for publishing and consuming messages"""

    QUEUE_NAME = 'attendance_events'

    def __init__(self, host: str = None):
        self.host = host or os.getenv('RABBITMQ_HOST', 'localhost')
        self.connection = None
        self.channel = None
        self._connect()

    def _connect(self):
        """Connect to RabbitMQ server"""
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.host)
            )
            self.channel = self.connection.channel()

            # Declare the queue
            self.channel.queue_declare(queue=self.QUEUE_NAME, durable=True)

            print(f"[RabbitMQ] Connected to {self.host}")
            print(f"[RabbitMQ] Queue '{self.QUEUE_NAME}' ready")
        except Exception as e:
            print(f"[RabbitMQ] Failed to connect: {e}")
            raise

    def publish(self, message: dict):
        """
        Publish a message to the attendance_events queue.

        Args:
            message: Dictionary with event data (will be JSON encoded)
        """
        try:
            self.channel.basic_publish(
                exchange='',
                routing_key=self.QUEUE_NAME,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json'
                )
            )
            print(f"[RabbitMQ] Published event: student={message.get('student_id')}, course={message.get('course_id')}")
        except Exception as e:
            print(f"[RabbitMQ] Failed to publish: {e}")
            # Try to reconnect
            try:
                self._connect()
                self.channel.basic_publish(
                    exchange='',
                    routing_key=self.QUEUE_NAME,
                    body=json.dumps(message),
                    properties=pika.BasicProperties(delivery_mode=2)
                )
                print(f"[RabbitMQ] Published event after reconnect")
            except:
                print(f"[RabbitMQ] Publish failed even after reconnect")

    def consume(self, callback: Callable):
        """
        Start consuming messages from the attendance_events queue.
        This blocks - run in a separate thread.

        Args:
            callback: Function to call for each message.
                      Signature: callback(channel, method, properties, body)
        """
        try:
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=self.QUEUE_NAME,
                on_message_callback=callback,
                auto_ack=False
            )
            print(f"[RabbitMQ] Waiting for events on '{self.QUEUE_NAME}'...")
            self.channel.start_consuming()
        except Exception as e:
            print(f"[RabbitMQ] Consumer error: {e}")

    def close(self):
        """Close connection"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            print("[RabbitMQ] Connection closed")

    def is_connected(self):
        """Check if connected to RabbitMQ"""
        return self.connection is not None and not self.connection.is_closed
