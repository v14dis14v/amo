from typing import Union

from entities._amo_abstract_entity import AmoAbstract
from entities import *


class Amo(AmoAbstract):
    """
    Основной класс для работы с amoCRM
    """

    def __init__(self, url: str, tokens: dict = {}, integration_data: dict = {}) -> None:
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
        """
        Получение информации об аккаунте

        :param account_with: Параметры запроса данных аккаунта
        :return: dict
        """
        data = {}

        if account_with != None:
            data['with'] = account_with

        return self._requesting('api/v4/account', self._method_get, params=data)

    def combine_some_unused_fields(self,
                                   custom_fields: Union[dict, list],
                                   fields: Union[list, str],
                                   is_email: bool = True) -> dict:
        """
        Ищет неисползуемые элементы в кастомных полях и если они есть, то комбинирует с уже имеющимися кастомными полями

        :param custom_fields: Кастомные поля
        :param fields:
        :param is_email:
        :return: dict
        """
        cf_data = {}

        if 'custom_fields_values' in custom_fields:
            custom_fields = custom_fields['custom_fields_values']

        if not custom_fields:
            return cf_data

        field_code = 'EMAIL' if is_email else 'PHONE'

        if isinstance(fields, str):
            fields = [fields if is_email else self.phone_clear(fields)]
        elif isinstance(fields, list) and not is_email:
            fields = [self.phone_clear(phone) for phone in fields]

        for custom_field in custom_fields:
            if custom_field['field_code'] == field_code:
                updated = False
                cf_id = custom_field['field_id']
                entity_fields = custom_field['values']

                cf_data[cf_id] = entity_fields
                entity_fields_values = [
                    entity_field['value'] if is_email
                    else self.phone_clear(entity_field['value']) for entity_field in entity_fields]

                for field in fields:
                    if not field in entity_fields_values:
                        cf_data[cf_id].append({'value': field, 'enum_code': 'WORK'})
                        updated = True

                return cf_data if updated else dict()

        return cf_data

    def get_custom_fields_value(self, custom_fields: dict, id: int, all_values: bool = False):
        """
        Получение значения кастомного поля

        :param custom_fields: Словарь кастомных полей
        :param id: Идентификатор кастомного поля
        :param all_values: Флаг означающий, что вернуть нужно не значение а все элементы кастомного поля
        :return: mixed
        """
        if not custom_fields:
            return False

        if 'custom_fields_values' in custom_fields:
            custom_fields = custom_fields['custom_fields_values']

        for custom_field in custom_fields:
            if custom_field['field_id'] == id:
                return custom_field['values'] if all_values else custom_field['values'][0]['value']

        return False

    def set_save_tokens(self, save_tokens: callable) -> None:
        """
        Переопределение метода сохранения токенов в БД

        :param save_tokens: Функция для переопределения метода сохранения токенов в БД
        :return: None
        """
        AmoAbstract.save_tokens = save_tokens

    def set_user(self, user) -> None:
        """
        Переопределение атрибута "пользователь"

        :param user: Объект пользователя
        :return: None
        """
        AmoAbstract.user = user
