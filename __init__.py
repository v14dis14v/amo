from amo_abstract_entity import AmoAbstract
from entities import *
import pprint


class Amo(AmoAbstract):
    """
    Основной класс для работы с amoCRM
    """

    def __init__(self, url: str, tokens: tuple = None, integration_data: dict = None) -> None:
        super().__init__(url, tokens, integration_data)

        self.contact = Contact(url, tokens, integration_data)
        self.company = Company(url, tokens, integration_data)
        self.lead = Lead(url, tokens, integration_data)
        self.task = Task(url, tokens, integration_data)
        self.note = Note(url, tokens, integration_data)
        self.unsorted = Unsorted(url, tokens, integration_data)

    def auth(self, code: str, refresh: bool = True):
        return super()._auth(code, refresh)