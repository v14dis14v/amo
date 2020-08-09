from entities._amo_abstract_entity import AmoAbstract
from entities import *


class Amo(AmoAbstract):
    """
    Основной класс для работы с amoCRM
    """

    def __init__(self, url: str, tokens: tuple = None, integration_data: dict = None) -> None:
        super().__init__(url, tokens, integration_data)

        self.contacts = Contacts(url, tokens, integration_data)
        self.companies = Companies(url, tokens, integration_data)
        self.leads = Leads(url, tokens, integration_data)
        self.tasks = Tasks(url, tokens, integration_data)
        self.notes = Notes(url, tokens, integration_data)
        self.unsorted = Unsorted(url, tokens, integration_data)

    def auth(self, code: str, refresh: bool = True):
        return super()._auth(code, refresh)