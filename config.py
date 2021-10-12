import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_CONFIG = {
    "url": os.getenv("DATABASE_URL"),
    "db_name": os.getenv("DATABASE_NAME"),
}
CELERY_CONFIG = {
    "broker": os.getenv("BROKER"),
    "backend": os.getenv("BACKEND"),
}

CRAWLER_CONFIG = {
    "MAX_RETRY": int(os.getenv("CRAWLER_MAX_RETRY")),
    "SLEEP_TIME": int(os.getenv("CRAWLER_SLEEP_TIME")),
}


FLASK_CONFIG = {
    "DEBUG": os.getenv("FLASK_DEBUG")
}
