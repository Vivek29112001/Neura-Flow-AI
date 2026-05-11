import logging
import os
from datetime import datetime

def setup_logger(name: str = "NeuraFlow") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console — UTF-8 fix for Windows
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    console.stream = open(
        os.devnull if False else 1,
        'w',
        encoding='utf-8',
        closefd=False
    )

    # File handler — saves daily log
    os.makedirs("logs", exist_ok=True)
    file_handler = logging.FileHandler(
        f"logs/neuraflow_{datetime.now().strftime('%Y%m%d')}.log",
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console)
    logger.addHandler(file_handler)

    return logger