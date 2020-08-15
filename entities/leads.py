from entities._amo_abstract_entity import AmoAbstract
from typing import Union
from datetime import datetime


class Leads(AmoAbstract):
    """
    Класс для работы с сущностью Сделка
    """

    def add(self,
            name: str,
            price: int = None,
            status_id: Union[dict, int] = None,
            user_id: int = None,
            custom_fields: dict = None,
            tags: dict = None
            ) -> int:
        """
        Создание 1 Сделки
        :param name: Название Сделки
        :param price: Бюджет
        :param status_id: Статус(можно указать словарь {pipeline_id: status_id})
        :param user_id: Ответственный за Сделку
        :param custom_fields: Кастомные поля {cf_id: {'vale': value}}
        :param tags: Тэги

        :return: int: id созданной Сдлеки
        """
        data = {'name': name}

        if price != None:
            data['price'] = price
        if isinstance(status_id, dict):
            data['pipeline_id'] = next(iter(status_id))
            data['status_id'] = status_id[data['pipeline_id']]
        elif status_id:
            data['status_id'] = status_id
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

    def update(self,
               id: int,
               name: str = None,
               price: int = None,
               status_id: Union[dict, int] = None,
               user_id: int = None,
               custom_fields: dict = None,
               tags: dict = None) -> dict:
        """
        Создание 1 Сделки
        :param name: Название Сделки
        :param price: Бюджет
        :param status_id: Статус(можно указать словарь {pipeline_id: status_id})
        :param user_id: Ответственный за Сделку
        :param custom_fields: Кастомные поля {cf_id: {'vale': value}}
        :param tags: Тэги

        :return: int: id созданной Сдлеки
        """
        data = {'id': id}

        if name != None:
            data['name'] = name
        if price != None:
            data['price'] = price
        if isinstance(status_id, dict):
            data['pipeline_id'] = next(iter(status_id))
            data['status_id'] = status_id[data['pipeline_id']]
        elif status_id:
            data['status_id'] = status_id
        if user_id != None:
            data['responsible_user_id'] = user_id
        if custom_fields != None:
            data['custom_fields_values'] = self._map_custom_fields(custom_fields)
        if tags != None:
            data['_embedded']['tags'] = []
            for tag_id, tag in tags.items():
                data['_embedded']['tags'].append({'id': tag_id, 'name': tag})

        return self._some_entity_request(method=self._method_post, params=[data])

    def get(self,
            id: int,
            lead_with: str = None,
            query: Union[str, int] = None,
            filter: dict = None,
            order: dict = None) -> dict:
        """
        Запрос 1 Сделки по её id

        :param id: Id Сделки
        :param lead_with: Данный параметр принимает строку, в том числе из нескольких значений, указанных через запятую.

        :return: dict
        """
        params = {}

        if lead_with != None:
            params['with'] = lead_with
        if query != None:
            params['query'] = query
        if filter != None:
            params['filter'] = filter
        if order != None:
            params['order'] = order
        return self._some_entity_request(self._method_get, params, str(id), strip_response=False)

    def getList(self,
                lead_with: str = None,
                query: Union[str, int] = None,
                filter: dict = None,
                order: dict = None) -> list:
        """
        Запрос всех Сделок
        :param lead_with: Данный параметр принимает строку, в том числе из нескольких значений, указанных через запятую.
        :param query: Поисковый запрос (Осуществляет поиск по заполненным полям сущности)
        :param filter: Фильтры
        :param order: Сортировка результатов списка.
                        Доступные поля для сортировки: created_at, updated_at, id.
                        Доступные значения для сортировки: asc, desc.
                        Пример: /api/v4/leads?order[updated_at]=asc

        :return: list
        """
        params = {'page': 1, 'limit': 250}
        results = []

        if lead_with != None:
            params['with'] = lead_with
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

    def link(self, id_from: int, to_entity: str, to_id: int, metadata: dict = None, link: bool = True) -> dict:
        """Привязывает сущность к Сделке"""
        return self._link_entities(id_from, to_entity, to_id, metadata, link)

    def links(self, id_from: int, data: list) -> dict:
        """Массовая привязка сущностей к Сделке"""
        return self._links_entities(id_from, data)

    def add_note(self, text: str, id: int, note_type: str = 'common', user: int = None, created_by: int = None) -> int:
        """Создание примечания в Сделку"""
        return self._add_some_entity_note(text, id, note_type, user, created_by)

    def add_task(self, text: str, id: int, task_type: int, complete_till: datetime, user: int = None) -> int:
        """Создание примечания в Сделку"""
        return self._add_some_entity_task(text, id, task_type, complete_till, user)
