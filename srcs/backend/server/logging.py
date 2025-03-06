import logging

logger = logging.getLogger("django.custom")

logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(message)s")
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)


