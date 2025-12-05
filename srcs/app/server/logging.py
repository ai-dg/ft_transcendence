import logging

# logger = logging.getLogger("django.custom")
logger = logging.getLogger("server.logging")

logger.info("\033[32m😉​TEST TRASCENDANCE LOG\033[0m")

logger.error("TEST OF ERRORS")

logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(message)s")
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)




