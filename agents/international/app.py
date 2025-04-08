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
        self.connect_to_rabbitmq()
        self.load_model()
        
    def connect_to_redis(self):
        """Connect to Redis for session management and caching"""
        redis_url = os.getenv("REDIS_URL", "redis://:password@redis:6379/0")
        self.redis_client = redis.from_url(redis_url)
        logger.info("Connected to Redis")
        
    def connect_to_rabbitmq(self):
        """Connect to RabbitMQ for message handling"""
        rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://pelephone:password@rabbitmq:5672/")
        
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
            except pika.exceptions.AMQPConnectionError:
                if attempt < max_retries - 1:
                    logger.warning(f"Failed to connect to RabbitMQ. Retrying in 5 seconds... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(5)
                else:
                    logger.error("Failed to connect to RabbitMQ after multiple attempts")
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
        # In a real implementation, this would interact with the AI model
        # Sample implementation:
        customer_id = request.get('customer_id')
        inquiry = request.get('inquiry')
        
        # Simulated processing
        logger.info(f"Processing billing inquiry for customer {customer_id}: {inquiry}")
        
        # Get customer billing information from cache or database
        customer_info = self.get_customer_info(customer_id)
        
        # Formulate response
        return {
            'status': 'success',
            'response': f"Processed billing inquiry regarding {inquiry}",
            'request_id': request.get('request_id'),
            'customer_info': customer_info
        }
    
    def handle_usage_discrepancy(self, request):
        """Analyze and resolve usage table discrepancies"""
        customer_id = request.get('customer_id')
        reported_usage = request.get('reported_usage')
        billed_usage = request.get('billed_usage')
        
        # Analyze the discrepancy
        logger.info(f"Analyzing usage discrepancy for customer {customer_id}")
        
        # Simulate discrepancy analysis
        discrepancy = billed_usage - reported_usage
        if discrepancy > 0:
            resolution = {
                'action': 'credit',
                'amount': discrepancy,
                'reason': 'Usage discrepancy correction'
            }
        else:
            resolution = {
                'action': 'verified',
                'message': 'Billing is correct based on usage records'
            }
        
        return {
            'status': 'success',
            'resolution': resolution,
            'request_id': request.get('request_id')
        }
    
    def handle_refund_request(self, request):
        """Process refund and credit requests"""
        customer_id = request.get('customer_id')
        refund_amount = request.get('amount')
        reason = request.get('reason')
        
        logger.info(f"Processing refund request for customer {customer_id}: ${refund_amount}")
        
        # Check refund eligibility
        if refund_amount > 100:
            # Escalate to supervisor for approval
            self.notify_supervisor(request, escalation="Large refund request")
            return {
                'status': 'pending',
                'message': 'Refund request escalated to supervisor for approval',
                'request_id': request.get('request_id')
            }
        
        # Process refund
        return {
            'status': 'success',
            'action': 'refund_approved',
            'amount': refund_amount,
            'reason': reason,
            'request_id': request.get('request_id')
        }
    
    def handle_plan_change(self, request):
        """Handle plan change requests and suggestions"""
        customer_id = request.get('customer_id')
        current_plan = request.get('current_plan')
        requested_plan = request.get('requested_plan')
        
        logger.info(f"Processing plan change from {current_plan} to {requested_plan} for customer {customer_id}")
        
        # Check if the requested plan exists
        if requested_plan not in self.get_available_plans():
            return {
                'status': 'error',
                'message': f"Plan {requested_plan} does not exist",
                'request_id': request.get('request_id')
            }
        
        # Process plan change
        return {
            'status': 'success',
            'action': 'plan_changed',
            'old_plan': current_plan,
            'new_plan': requested_plan,
            'effective_date': '2023-10-01',  # Example date
            'request_id': request.get('request_id')
        }
    
    def notify_supervisor(self, request, error=None, escalation=None):
        """Notify the supervisor agent about errors or escalations"""
        notification = {
            'source': 'billing_agent',
            'timestamp': time.time(),
            'request': request,
            'error': error,
            'escalation': escalation
        }
        
        self.channel.basic_publish(
            exchange='',
            routing_key='supervisor_notifications',
            body=json.dumps(notification),
            properties=pika.BasicProperties(
                delivery_mode=2  # make message persistent
            )
        )
        logger.info("Supervisor notified")
    
    def get_customer_info(self, customer_id):
        """Get customer information from cache or database"""
        # Try to get from cache first
        cached_info = self.redis_client.get(f"customer:{customer_id}")
        if cached_info:
            return json.loads(cached_info)
        
        # If not in cache, this would normally fetch from the database
        # For this example, we'll return mock data
        customer_info = {
            'id': customer_id,
            'name': 'John Doe',
            'plan': 'Premium 100GB',
            'monthly_charge': 99.99,
            'contract_end_date': '2024-06-30',
            'last_bill_amount': 105.42,
            'payment_status': 'current'
        }
        
        # Store in cache for future use
        self.redis_client.setex(
            f"customer:{customer_id}",
            3600,  # 1 hour expiration
            json.dumps(customer_info)
        )
        
        return customer_info
    
    def get_available_plans(self):
        """Get list of available plans"""
        # Try to get from cache
        cached_plans = self.redis_client.get("available_plans")
        if cached_plans:
            return json.loads(cached_plans)
        
        # Mock data for available plans
        plans = [
            'Basic 5GB',
            'Standard 20GB',
            'Premium 100GB',
            'Unlimited Data',
            'Family Plan 50GB',
            'Business Pro 200GB'
        ]
        
        # Store in cache
        self.redis_client.setex(
            "available_plans",
            86400,  # 24 hour expiration
            json.dumps(plans)
        )
        
        return plans
    
    def run(self):
        """Start consuming messages"""
        logger.info("Billing Agent is running. Waiting for messages...")
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
            self.connection.close()
            logger.info("Billing Agent stopped")

if __name__ == "__main__":
    # Wait for a short period to ensure RabbitMQ is ready
    time.sleep(10)
    
    agent = BillingAgent()
    agent.run()