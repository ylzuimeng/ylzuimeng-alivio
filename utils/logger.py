import logging

logging.basicConfig(
    filename='process.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

def log_success(task, msg):
    logging.info(f"SUCCESS: {task} - {msg}")

def log_failure(task, reason):
    logging.error(f"FAIL: {task} - {reason}")

def log_info(msg):
    logging.info(msg) 