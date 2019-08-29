from multiprocessing import Process, Queue

import pygame

from core.data_retriever import DataRetriever
from core.data_presenter import DataPresenter

CONFIG_FILE = 'config.ini'

pygame.init()

if __name__ == '__main__':
    queue_retriever = Queue()
    queue_presenter = Queue()

    data_retriever = DataRetriever(CONFIG_FILE, queue_retriever)
    data_presenter = DataPresenter(CONFIG_FILE, queue_presenter)
    p_retrieve = Process(target=data_retriever.run)
    p_present = Process(target=data_presenter.run)
    p_retrieve.start()
    p_present.start()

    obj = queue_presenter.get()
    queue_retriever.put("halt")

    queue_retriever.close()
    queue_presenter.close()
    queue_retriever.join_thread()
    queue_presenter.join_thread()

    p_present.join()
    p_retrieve.join()

    pygame.quit()
