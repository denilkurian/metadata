import os
import logging

def configure_logging():
    log_folder = "logging_service"  
    os.makedirs(log_folder, exist_ok=True)
    log_file_path = os.path.join(log_folder, "app.log")
    logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(threadName)s : %(message)s')

# Trying to add a error middleware that captures all the errors automatically and add to logs
async def error_middleware(request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logging.error(f"An error occurred while processing request: {e}")
        raise












