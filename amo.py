from entities._amo_abstract_entity import AmoAbstract
from entities import *


class Amo(AmoAbstract):
    """
    Основной класс для работы с amoCRM
    """

    def __init__(self, url: str, tokens: dict = None, integration_data: dict = None) -> None:
        super().__init__(url, tokens, integration_data)

        self.contacts = Contacts(url, tokens, integration_data)
        self.companies = Companies(url, tokens, integration_data)
        self.leads = Leads(url, tokens, integration_data)
        self.tasks = Tasks(url, tokens, integration_data)
        self.notes = Notes(url, tokens, integration_data)
        self.unsorted = Unsorted(url, tokens, integration_data)
        self.catalogs = Catalogs(url, tokens, integration_data)

    def auth(self, code: str, refresh: bool = True) -> dict:
        """
        Обмен ключей в amo
        :param code: Код обмена
        :param refresh: Ключ обозначачающий, что это обмен ревреш токена
        :return:
        """
        return super()._auth(code, refresh)

    def get_account(self, account_with: str = None) -> dict:
        data = {}

        if account_with != None:
            data['with'] = account_with

        return self._requesting('api/v4/account', self._method_get, params=data)

    def set_save_tokens(self, save_tokens: callable):
        AmoAbstract.save_tokens = save_tokens

    def set_user(self, user):
        AmoAbstract.user = user
