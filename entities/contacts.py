from typing import Union

from entities._amo_abstract_entity import AmoAbstract


class Contacts(AmoAbstract):
    """
    Класс для работы с сущностью Контакт
    """

    def add(self, name: Union[str, tuple], user_id: int = None, custom_fields: dict = None, tags: dict = None) -> int:
        """
        Создание 1 Контакта
        :param name: Название Контакта Если (string) то запишется в поле 'name',
                                    если (array) то [0] => 'first_name', [1] => 'last_name'
        :param user_id: Ответственный за Контакт
        :param custom_fields: Кастомные поля {cf_id: {'vale': value}}
        :param tags: Тэги

        :return: int: id созданного Контакта
        """
        data = {}

        if isinstance(name, str):
            data['name'] = name
        else:
            if 0 in name and name[0]:
                data['first_name'] = name[0]
                data['last_name'] = None if not 1 in name else name[1]
            elif 1 in name and name[1]:
                data['name'] = name[1]

        if user_id != None:
            data['responsible_user_id'] = user_id
        if custom_fields != None:
            data['custom_fields_values'] = self._map_custom_fields(custom_fields)
        if tags != None:
            data['_embedded']['tags'] = []
            for tag_id, tag in tags.items():
                data['_embedded']['tags'].append({'id': tag_id, 'name': tag})

        response = self._some_entity_request(method=self._method_post, params=[data])

        return response[0]['id']

    def update(self, id: int,
               name: Union[str, tuple] = None,
               user_id: int = None,
               custom_fields: dict = None,
               tags: dict = None) -> dict:
        data = {'id': id}

        if name != None:
            if isinstance(name, str):
                data['name'] = name
            else:
                if 0 in name and name[0]:
                    data['first_name'] = name[0]
                    data['last_name'] = None if not 1 in name else name[1]
                elif 1 in name and name[1]:
                    data['name'] = name[1]

        if user_id != None:
            data['responsible_user_id'] = user_id
        if custom_fields != None:
            data['custom_fields_values'] = self._map_custom_fields(custom_fields)
        if tags != None:
            data['_embedded']['tags'] = []
            for tag_id, tag in tags.items():
                data['_embedded']['tags'].append({'id': tag_id, 'name': tag})

        return self._some_entity_request(method=self._method_patch, params=[data])

    def get(self,
            id: int,
            contact_with: str = None,
            query: Union[str, int] = None,
            filter: dict = None,
            order: dict = None) -> dict:
        """
        Запрос 1 Контакта по его id

        :param id: Id Контакта
        :param contact_with: Данный параметр принимает строку, в том числе из нескольких значений, указанных через запятую.

        :return: dict
        """
        params = {}

        if contact_with != None:
            params['with'] = contact_with
        if query != None:
            params['query'] = query
        if filter != None:
            params['filter'] = filter
        if order != None:
            params['order'] = order

        return self._some_entity_request(self._method_get, params, str(id), strip_response=False)

    def getList(self,
                contact_with: str = None,
                query: Union[str, int] = None,
                filter: dict = None,
                order: dict = None) -> list:
        """
        Запрос всех Контактов
        :param contact_with: Данный параметр принимает строку, в том числе из нескольких значений, указанных через запятую.
        :param query: Поисковый запрос (Осуществляет поиск по заполненным полям сущности)
        :param filter: Фильтры
        :param order: Сортировка результатов списка.
                        Доступные поля для сортировки: created_at, updated_at, id.
                        Доступные значения для сортировки: asc, desc.
                        Пример: /api/v4/contacts?order[updated_at]=asc

        :return: list
        """
        params = {'page': 1, 'limit': 250}
        results = []

        if contact_with != None:
            params['with'] = contact_with
        if query != None:
            params['query'] = query
        if filter != None:
            params['filter'] = filter
        if order != None:
            params['order'] = order

        while True:
            response = self._some_entity_request(method=self._method_get, params=params)
            results.extend(response)
            params['page'] += 1

            if len(response) < 250:
                break

        return results

    def delete(self):
        pass

    def find_by_email(self, email: str) -> dict:
        """"
        Ищет Контакт по email
        :param email: Мыло

        :return dict Контакт
        """
        contacts = self.getList('catalog_elements,leads,customers', email)
        for contact in contacts:
            for cf in contact['custom_fields_values']:
                if 'field_code' in cf and cf['field_code'] == 'EMAIL':
                    for value in cf['values']:
                        if email.lower() == value['value'].lower():
                            return contact

        return {}

    def find_by_phone(self, phone: str) -> dict:
        """"
        Ищет Контакт по email
        :param phone: Телефон

        :return dict Контакт
        """
        clear_phone = self.phone_clear(phone)
        if len(clear_phone) < 5:
            return {}

        contacts = self.getList('catalog_elements,leads,customers', phone)
        for contact in contacts:
            for cf in contact['custom_fields_values']:
                if 'field_code' in cf and cf['field_code'] == 'PHONE':
                    for value in cf['values']:
                        if clear_phone == self.phone_clear(value['value']):
                            return contact

        return {}

    def add_note(self, text: str, id: int, note_type: str = 'common', user: int = None, created_by: int = None) -> int:
        """Создание примечания в Контакт"""
        return self._add_some_entity_note(text, id, note_type, user, created_by)
