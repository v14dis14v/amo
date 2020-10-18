from typing import Union

from entities._amo_abstract_entity import AmoAbstract


class Companies(AmoAbstract):
    """
    Класс для работы с сущностью Компания
    """

    def add(self,
            name: str,
            user_id: int = None,
            custom_fields: dict = None,
            tags: dict = None
            ) -> int:
        """
        Создание 1 Компании
        :param name: Название Компании
        :param user_id: Ответственный за Компанию
        :param custom_fields: Кастомные поля {cf_id: {'vale': value}}
        :param tags: Тэги

        :return: int: id созданной Сдлеки
        """
        data = {'name': name}
        if user_id != None:
            data['responsible_user_id'] = int
        if custom_fields != None:
            data['custom_fields_values'] = self._map_custom_fields(custom_fields)
        if tags != None:
            data['_embedded']['tags'] = []
            for tag_id, tag in tags.items():
                data['_embedded']['tags'].append({'id': tag_id, 'name': tag})

        response = self._some_entity_request(method=self._method_post, params=[data])

        return response[0]['id']

    def update(self,
               id: int,
               name: str,
               user_id: int = None,
               custom_fields: dict = None,
               tags: dict = None) -> dict:

        data = {'id': id}

        if name != None:
            data['name'] = name
        if user_id != None:
            data['responsible_user_id'] = int
        if custom_fields != None:
            data['custom_fields_values'] = self._map_custom_fields(custom_fields)
        if tags != None:
            data['_embedded']['tags'] = []
            for tag_id, tag in tags.items():
                data['_embedded']['tags'].append({'id': tag_id, 'name': tag})

        return self._some_entity_request(method=self._method_post, params=[data])

    def get(self,
            id: int,
            company_with: str = None,
            query: Union[str, int] = None,
            filter: dict = None,
            order: dict = None) -> dict:
        """
        Запрос 1 Компании по его id

        :param id: Id Контакта
        :param company_with: Данный параметр принимает строку, в том числе из нескольких значений, указанных через запятую.

        :return: dict
        """
        params = {}

        if company_with != None:
            params['with'] = company_with
        if query != None:
            params['query'] = query
        if filter != None:
            params['filter'] = filter
        if order != None:
            params['order'] = order

        return self._some_entity_request(self._method_get, params, str(id), strip_response=False)

    def getList(self,
                company_with: str = None,
                query: Union[str, int] = None,
                filter: dict = None,
                order: dict = None) -> list:
        """name
        Запрос всех Компаний
        :param company_with: Данный параметр принимает строку, в том числе из нескольких значений, указанных через запятую.
        :param query: Поисковый запрос (Осуществляет поиск по заполненным полям сущности)
        :param filter: Фильтры
        :param order: Сортировка результатов списка.
                        Доступные поля для сортировки: created_at, updated_at, id.
                        Доступные значения для сортировки: asc, desc.
                        Пример: /api/v4/companies?order[updated_at]=asc

        :return: list
        """
        params = {'page': 1, 'limit': 250}
        results = []

        if company_with != None:
            params['with'] = company_with
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

            if len(response) < params['limit']:
                break

        return results

    def delete(self):
        pass

    def add_note(self, text: str, id: int, note_type: str = 'common', user: int = None, created_by: int = None) -> int:
        """Создание примечания в Компанию"""
        return self._add_some_entity_note(text, id, note_type, user, created_by)
