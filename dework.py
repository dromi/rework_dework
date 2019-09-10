from configparser import ConfigParser
from multiprocessing import Process, Queue

import pygame

from core.data_retriever import DataRetriever
from core.data_presenter import DataPresenter
from core.logging_filters import create_logger

CONFIG_FILE = 'config.ini'

pygame.init()

if __name__ == '__main__':
    config = ConfigParser()
    config.read(CONFIG_FILE)
    logger = create_logger(config['general']['logging_path'], __name__)

    logger.info("Starting main application")

    queue_retriever = Queue()
    queue_presenter = Queue()

    data_retriever = DataRetriever(CONFIG_FILE, queue_retriever)
    data_presenter = DataPresenter(CONFIG_FILE, queue_presenter)
    p_retrieve = Process(target=data_retriever.run)
    p_present = Process(target=data_presenter.run)
    p_retrieve.start()
    p_present.start()

    obj = queue_presenter.get()
    logger.info("Received halting signal from presenter")
    logger.info("halting retriever")
    queue_retriever.put("halt")

    logger.info("Closing queues")
    queue_retriever.close()
    queue_presenter.close()
    queue_retriever.join_thread()
    queue_presenter.join_thread()

    logger.info("Joining processes")
    p_present.join()
    p_retrieve.join()

    logger.info("Quitting pygame")
    pygame.quit()
