import os
import redis
from rq import Worker, Queue
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="../.env.deco_security")

listen = ['default']

redis_url = os.getenv('REDIS_URL', 'redis://deco-sec-redis:6379')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    # Pass connection explicitly to Worker instead of using Connection context manager
    # This avoids potential import issues with different rq versions
    queues = [Queue(name, connection=conn) for name in listen]
    worker = Worker(queues, connection=conn)
    worker.work()
