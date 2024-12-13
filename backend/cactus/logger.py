import logging

logging.basicConfig(format='%(asctime)s\t%(levelname)s\t[%(name)s]\t%(message)s')
logger = logging.getLogger('cactus')
logger.setLevel(logging.INFO)
