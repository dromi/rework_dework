from multiprocessing import Process

from core.data_retriever import DataRetriever
from core.data_presenter import DataPresenter

CONFIG_FILE = 'config.ini'

if __name__ == '__main__':
    data_retriever = DataRetriever(CONFIG_FILE)
    data_presenter = DataPresenter(CONFIG_FILE)
    p_retrieve = Process(target=data_retriever.run)
    p_present = Process(target=data_presenter.run)
    p_retrieve.start()
    p_present.start()
