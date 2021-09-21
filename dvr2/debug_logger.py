import logging

def init_logger(_name, _level):
    logger = logging.getLogger(_name)
    
    if _level == 'info':
        logger.setLevel(logging.INFO)
        
    if _level == 'debug':
        logger.setLevel(logging.DEBUG)
        
    if _level == 'warning':
        logger.setLevel(logging.WARNING)
        
        
    # set the format to include the timestamp
    formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')
    # print to file @ cwd
    file_handler = logging.FileHandler('debug.log')
    file_handler.setFormatter(formatter)
    # print to console
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.info('logger initiated: cwd/debug.log')
    return logger
