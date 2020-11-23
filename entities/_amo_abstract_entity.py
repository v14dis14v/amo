from datetime import datetime
from typing import Union
from pprint import pformat
import requests
import re


class AmoAbstract:
    """
    Абстрактный класс сущностей amoCRM
    :var entity: string - название сущности
    """

    def __init__(self, url: str, tokens: dict = {}, integration_data: dict = {}) -> None:
        """
        Заполнение основных параметров объекта

        :param url: Главынй url от которого будут строится относительные пути
        :param tokens: Токены авторизации и обновления
        :param integration_data: Данные об интеграции
              {'integration_id' : '...', 'secret_key' : '...', 'redirect_url': 'www'}
        """
        self._base_url = 'https://' + url
        self._domain = url.split('.', 1)
        self._access_token = None if tokens is None else tokens['access_token']
        self._refresh_token = None if tokens is None else tokens['refresh_token']
        self._integration_id = integration_data['integration_id'] if 'integration_id' in integration_data else None
        self._secret_key = integration_data['secret_key'] if 'secret_key' in integration_data else None
        self._redirect_url = integration_data['redirect_url'] if 'redirect_url' in integration_data else None

        self._method_get = requests.get
        self._method_post = requests.post
        self._method_patch = requests.patch
        self._method_delete = requests.delete

    def _requesting(self,
                    path: str,
                    requester: callable,
                    json: Union[dict, list] = None,
                    params: dict = None,
                    headers: dict = None,
                    hand_brake: bool = False) -> dict:
        """
        Самый главный курлык на районе

        :param path: Относительный api путь
        :param requester:
        :param params: Параметры запросы
        :param headers: Заголовки запроса
        :param hand_brake: Ручник для остановки запросов, нужен при повторных запросах при обновлении ключей
        """

        headers_without_token = headers

        if self._access_token != None:
            base_headers = {'authorization': 'Bearer ' + self._access_token}
            headers = base_headers if headers == None else dict(**headers, **base_headers)

        response = requester(f'{self._base_url}/{path}', params=params, json=json, headers=headers)

        if response.status_code == 204:
            return {}

        if response.status_code == 401 and self._refresh_token and not hand_brake:
            tokens = self._auth(self._refresh_token, True)

            if not 'access_token' in tokens or not 'refresh_token' in tokens:
                raise AmoException(f'Auth Error. \n url > {response.url}')

            self._access_token = tokens['access_token']
            self._refresh_token = tokens['refresh_token']

            if self.check_auth():
                self.save_tokens()

            return self._requesting(path, requester, json, params, headers_without_token, True)
        if response.status_code < 200 or response.status_code > 204:
            response_json = '' if not response.text else response.json()

            raise AmoException(f'Request Error: '
                               f'\n URL -> {response.url} '
                               f'\n Method -> {requester.__name__} '
                               f'\n Request Params -> {pformat(params)}'
                               f'\n Request Json -> {pformat(json)}'
                               f'\n Response Json -> {pformat(response_json)}'
                               f'\n Headers -> {pformat(headers_without_token)}')

        return response.json()

    def check_auth(self) -> bool:
        """Проверка правильности ключей"""
        response = self._requesting('api/v4/account', self._method_get, hand_brake=True)

        return True if 'id' in response else False

    def _auth(self, code: str, refresh: bool = True) -> dict:
        """
        Обмен кода авторизации на ключи

        :param code: Код для получения ключей
        :param refresh: Ключ обозначающий что это обновление

        :return dict
        """
        json_params = {
            'client_id': self._integration_id,
            'client_secret': self._secret_key,
            'grant_type': 'refresh_token' if refresh else 'authorization_code',
            'redirect_uri': self._redirect_url,
        }

        if refresh:
            json_params['refresh_token'] = code
        else:
            json_params['code'] = code

        response = self._requesting('oauth2/access_token', requests.post, json_params, hand_brake=True)
        response = response['_embedded'] if '_embedded' in response else response

        if not 'access_token' in response or not 'refresh_token' in response:
            raise AmoException(response)

        self._access_token = response['access_token']
        self._refresh_token = response['refresh_token']

        return response

    def _map_custom_fields(self, custom_fields: dict) -> list:
        """
        Преобразует массив доп. полей в готовый для отправки по API и фильтрует пустые элементы массива,
        причем фильтрует обычные поля и мультисписки.
        :param custom_fields:

        :return: list
        """
        new_custom_fields = []

        for id, cf in custom_fields.items():
            if 'value' in cf and cf['value'] != None:
                tmp = {'value': cf['value']}

                if 'enum_id' in cf:
                    tmp['enum_id'] = cf['enum_id']

                if 'enum_code' in cf:
                    tmp['enum_code'] = cf['enum_code']

                if 'subtype' in cf:
                    tmp['subtype'] = cf['subtype']

                new_custom_fields.append({'field_id': id, 'values': [tmp]})
            elif isinstance(cf, list):
                cf_filter = []

                for value in cf:
                    if value == None:
                        continue

                    cf_filter.append(value)
                new_custom_fields.append({'field_id': id, 'values': cf_filter})

        return new_custom_fields

    def _some_entity_request(self,
                             method: callable,
                             params: dict = None,
                             add_url: str = None,
                             strip_response: bool = True):
        """
        Запрос в определённую сущность
        :param method:
        :param params:
        :param add_url:
        :param strip_response:
        :return:
        """
        entity = self.__class__.__name__.lower()
        lead_url = 'api/v4/' + entity
        json = None

        if add_url != None:
            lead_url += '/' + add_url
        if method.__name__ == 'post' or method.__name__ == 'patch':
            json = params
            params = None

        response = self._requesting(lead_url, method, params=params, json=json)

        return self._prepare_response(response, entity) if strip_response else response

    def _add_some_entity_note(self,
                              text: str,
                              id: int,
                              note_type: str = 'common',
                              user: int = None,
                              created_by: int = None
                              ) -> int:
        data = {'params': {'text': text}, 'note_type': note_type}

        if user != None:
            data['responsible_user_id'] = user
        if created_by != None:
            data['created_by'] = created_by

        response = self._some_entity_request(self._method_post, [data], str(id))

        return response[0]['id']

    def _add_some_entity_task(self,
                              text: str,
                              id: int,
                              task_type: int,
                              complete_till: datetime,
                              user: int = None) -> int:
        """
        Добавление Задачи в сущность
        :param text:
        :param id:
        :param task_type:
        :param complete_till:
        :param user:
        :return:
        """
        entity = self.__class__.__name__.lower()
        data = {
            'text': text,
            'entity_id': id,
            'entity_type': entity,
            'task_type_id': task_type,
            'complete_till': int(complete_till.timestamp())
        }

        if user != None:
            data['responsible_user_id'] = user

        response = self._requesting('api/v4/tasks', self._method_post, json=[data])

        return self._prepare_response(response, 'tasks')[0]['id']

    def phone_clear(self, phone: str) -> str:
        """
        Очистка телефона от лишних символов

        :param phone:
        :return:
        """

        return re.compile(r'[^\d]').sub('', phone)

    def _link_entities(self,
                       id_from: int,
                       to_entity: str,
                       to_id: int,
                       metadata: dict = None,
                       link: bool = True) -> dict:
        """
        Связка 1 сущности с дргуой
        :param id_from:
        :param to_entity:
        :param to_id:
        :param metadata:
        :param link:
        :return:
        """
        data = {'to_entity_id': to_id, 'to_entity_type': to_entity}

        if metadata:
            data['metadata'] = metadata

        return self._links_entities(id_from, [data], link)

    def _links_entities(self, id_from: int, data: list, link: bool = True) -> list:
        """
        Привязка между несколькими сущностями
        :param id_from:
        :param data:
        :param link:
        :return:
        """
        entity = self.__class__.__name__.lower()
        url = f'api/v4/{entity}/{int(id_from)}/' + ('link' if link else 'unlink')
        response = self._requesting(url, self._method_post, json=data)

        return self._prepare_response(response, 'links')

    def _get_custom_fields(self, id: int = None) -> list:
        url = 'custom_fields' + (f'/{id}' if id else '')
        params = {'page': 1, 'limit': 250}
        results = []

        while True:
            response = self._some_entity_request(method=self._method_get, params=params, add_url=url)
            if 'custom_fields' in response:
                response = response['custom_fields']

            results.extend(response)
            params['page'] += 1

            if len(response) < params['limit']:
                break
        return results

    def _update_custom_field(self, id: int, name: str = None, options: dict = None):
        url = f'custom_fields/{id}'
        params = {}

        if name:
            params['name'] = name

        if options:
            if 'code' in options:
                params['code'] = options['code']
            if 'sort' in options:
                params['sort'] = options['sort']
            if 'group_id' in options:
                params['group_id'] = options['group_id']
            if 'is_api_only' in options:
                params['is_api_only'] = options['is_api_only']
            if 'required_statuses' in options:
                params['required_statuses'] = options['required_statuses']
            if 'settings' in options:
                params['settings'] = options['settings']
            if 'is_visible' in options:
                params['is_visible'] = options['is_visible']
            if 'is_required' in options:
                params['is_required'] = options['is_required']
            if 'remind' in options:
                params['remind'] = options['remind']
            if 'enums' in options:
                params['enums'] = options['enums']
            if 'nested' in options:
                params['nested'] = options['nested']

        response = self._some_entity_request(self._method_patch, params, url)
        if 'custom_fields' in response:
            return response['custom_fields']

        return response

    def _prepare_response(self, response: dict, entity_key: str) -> dict:
        if '_embedded' in response:
            response = response['_embedded']

        if entity_key in response:
            response = response[entity_key]

        return response

    def save_tokens(self):
        """
        Абстрактный метод сохранения токенов
        :return:
        """
        pass


class AmoException(Exception):
    pass
