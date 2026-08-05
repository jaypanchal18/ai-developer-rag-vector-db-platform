import time
import logging
from fastapi import FastAPI, Request
from prometheus_client import start_http_server, Summary, Counter, Histogram
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# Initialize FastAPI app
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('request_count', 'Total number of requests')
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency in seconds')
DB_QUERY_COUNT = Counter('db_query_count', 'Total number of database queries')
DB_QUERY_LATENCY = Histogram('db_query_latency_seconds', 'Database query latency in seconds')

# Database connection
DATABASE_URL = "postgresql://user:password@localhost/dbname"
engine = create_engine(DATABASE_URL)

# Start Prometheus metrics server
start_http_server(8000)

@app.middleware("http")
async def add_metrics(request: Request, call_next):
    start_time = time.time()
    REQUEST_COUNT.inc()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    REQUEST_LATENCY.observe(duration)
    
    return response

@app.get("/metrics")
async def get_metrics():
    return {
        "request_count": REQUEST_COUNT._value.get(),
        "request_latency": REQUEST_LATENCY._sum.get(),
    }

def execute_db_query(query: str):
    try:
        with engine.connect() as connection:
            start_time = time.time()
            result = connection.execute(query)
            DB_QUERY_COUNT.inc()
            DB_QUERY_LATENCY.observe(time.time() - start_time)
            return result
    except SQLAlchemyError as e:
        logger.error(f"Database query failed: {e}")
        return None

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the application...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down the application...")