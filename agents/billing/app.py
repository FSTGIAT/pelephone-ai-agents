import os
import json
import logging
import pika
import redis
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("BillingAgent")

class BillingAgent:
    """
    Billing Agent responsible for:
    1. Resolving billing issues
    2. Analyzing discrepancies in usage tables and pricing
    3. Processing adjustments, refunds, and credits
    4. Answering billing-related questions
    """
    
    def __init__(self):
        self.connect_to_redis()
        try:
            self.connect_to_rabbitmq()
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            logger.info("Continuing without RabbitMQ connection")
        self.load_model()
        
    def connect_to_redis(self):
        """Connect to Redis for session management and caching"""
        redis_url = os.getenv("REDIS_URL", "redis://:password@redis:6379/0")
        try:
            self.redis_client = redis.from_url(redis_url)
            logger.info("Connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            self.redis_client = None
        
    def connect_to_rabbitmq(self):
        """Connect to RabbitMQ for message handling"""
        rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
        logger.info(f"Connecting to RabbitMQ with URL: {rabbitmq_url}")
        
        # Retry connection to RabbitMQ (useful during startup)
        max_retries = 5
        for attempt in range(max_retries):
            try:
                parameters = pika.URLParameters(rabbitmq_url)
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()
                
                # Declare queues
                self.channel.queue_declare(queue='billing_requests', durable=True)
                self.channel.queue_declare(queue='billing_responses', durable=True)
                self.channel.queue_declare(queue='supervisor_notifications', durable=True)
                
                # Set up consumer
                self.channel.basic_consume(
                    queue='billing_requests',
                    on_message_callback=self.process_request,
                    auto_ack=False
                )
                
                logger.info("Connected to RabbitMQ")
                break
            except pika.exceptions.AMQPConnectionError as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Failed to connect to RabbitMQ. Retrying in 5 seconds... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(5)
                else:
                    logger.error(f"Failed to connect to RabbitMQ after multiple attempts: {str(e)}")
                    raise
    
    def load_model(self):
        """Load the AI model for billing queries"""
        logger.info("Loading billing model...")
        # In a real implementation, we would load the model here
        # For example:
        # from transformers import AutoTokenizer, AutoModelForSequenceClassification
        # self.tokenizer = AutoTokenizer.from_pretrained("path/to/tokenizer")
        # self.model = AutoModelForSequenceClassification.from_pretrained("path/to/model")
        logger.info("Billing model loaded successfully")
    
    def process_request(self, ch, method, properties, body):
        """Process incoming billing requests"""
        try:
            request = json.loads(body)
            logger.info(f"Received billing request: {request.get('request_id')}")
            
            # Process the request based on type
            request_type = request.get('type', 'unknown')
            
            if request_type == 'billing_inquiry':
                response = self.handle_billing_inquiry(request)
            elif request_type == 'usage_discrepancy':
                response = self.handle_usage_discrepancy(request)
            elif request_type == 'refund_request':
                response = self.handle_refund_request(request)
            elif request_type == 'plan_change':
                response = self.handle_plan_change(request)
            else:
                logger.warning(f"Unknown request type: {request_type}")
                response = {
                    'status': 'error',
                    'message': f"Unknown request type: {request_type}",
                    'request_id': request.get('request_id')
                }
                
                # Notify supervisor about unknown request type
                self.notify_supervisor(request, error="Unknown request type")
            
            # Send response back
            self.channel.basic_publish(
                exchange='',
                routing_key='billing_responses',
                body=json.dumps(response),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                    correlation_id=properties.correlation_id,
                    reply_to=properties.reply_to
                )
            )
            
            # Acknowledge the message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"Processed request {request.get('request_id')}")
            
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            self.notify_supervisor({"error": str(e), "body": body.decode()}, error="Processing error")
    
    def handle_billing_inquiry(self, request):
        """Handle general billing inquiries"""
        # Sample implementation
        logger.info(f"Processing billing inquiry for customer {request.get('customer_id')}")
        return {
            'status': 'success',
            'response': 'Your billing inquiry has been processed',
            'request_id': request.get('request_id')
        }
    
    def handle_usage_discrepancy(self, request):
        """Analyze and resolve usage table discrepancies"""
        logger.info(f"Analyzing usage discrepancy for customer {request.get('customer_id')}")
        return {
            'status': 'success',
            'resolution': 'Discrepancy resolved',
            'request_id': request.get('request_id')
        }
    
    def handle_refund_request(self, request):
        """Process refund and credit requests"""
        logger.info(f"Processing refund request for customer {request.get('customer_id')}")
        return {
            'status': 'success',
            'action': 'refund_approved',
            'request_id': request.get('request_id')
        }
    
    def handle_plan_change(self, request):
        """Handle plan change requests and suggestions"""
        logger.info(f"Processing plan change for customer {request.get('customer_id')}")
        return {
            'status': 'success',
            'action': 'plan_changed',
            'request_id': request.get('request_id')
        }
    
    def notify_supervisor(self, request, error=None, escalation=None):
        """Notify the supervisor agent about errors or escalations"""
        if not hasattr(self, 'channel') or self.channel is None:
            logger.warning("Cannot notify supervisor: No RabbitMQ connection")
            return
            
        notification = {
            'source': 'billing_agent',
            'timestamp': time.time(),
            'request': request,
            'error': error,
            'escalation': escalation
        }
        
        try:
            self.channel.basic_publish(
                exchange='',
                routing_key='supervisor_notifications',
                body=json.dumps(notification),
                properties=pika.BasicProperties(
                    delivery_mode=2  # make message persistent
                )
            )
            logger.info("Supervisor notified")
        except Exception as e:
            logger.error(f"Failed to notify supervisor: {str(e)}")
    
    def run(self):
        """Start consuming messages"""
        logger.info("Billing Agent is running.")
        
        # If we don't have a RabbitMQ connection, just keep the container running
        if not hasattr(self, 'channel') or self.channel is None:
            logger.info("No RabbitMQ connection. Running in passive mode.")
            while True:
                time.sleep(60)
                logger.info("Billing Agent still running in passive mode...")
        else:
            logger.info("Waiting for messages...")
            try:
                self.channel.start_consuming()
            except KeyboardInterrupt:
                self.channel.stop_consuming()
                self.connection.close()
                logger.info("Billing Agent stopped")
            except Exception as e:
                logger.error(f"Error in message consumption: {str(e)}")

if __name__ == "__main__":
    # Wait for a short period to ensure dependencies are ready
    time.sleep(10)
    
    try:
        agent = BillingAgent()
        agent.run()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
