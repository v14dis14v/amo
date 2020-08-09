import requests
from amo_exception import AmoException


class AmoAbstract:
    """Абстрактный класс сущностей amoCRM"""

    def __init__(self, url: str, tokens: dict = None, integration_data: dict = None) -> None:
        """
        Заполнение основных параметров объекта

        :param url: Главынй url от которого будут строится относительные пути
        :param tokens: Токены авторизации и обновления
        :param integration_data: Данные об интеграции
              {'integration_id' : '...', 'secret_key' : '...', 'redirect_url': 'www'}
        """
        self.base_url = 'https://' + url
        self.domain = url.split('.', 1)
        self.access_token = None if tokens == None else tokens['access_token']
        self.refresh_token = None if tokens == None else tokens['refresh_token']
        self.integration_id = integration_data['integration_id'] if 'integration_id' in integration_data else None
        self.secret_key = integration_data['secret_key'] if 'secret_key' in integration_data else None
        self.redirect_url = integration_data['redirect_url'] if 'redirect_url' in integration_data else None

        self.method_get = requests.get
        self.method_post = requests.post
        self.method_put = requests.put
        self.method_delete = requests.delete

    def _requesting(self,
                    path: str,
                    requester: callable,
                    json: dict = None,
                    params: dict = None,
                    headers: dict = None,
                    hand_brake: bool = False):
        """
        Самый главный курлык на районе

        :param path: Относительный api путь
        :param requester:
        :param params: Параметры запросы
        :param headers: Заголовки запроса
        :param hand_brake: Ручник для остановки запросов, нужен при повторных запросах при обновлении ключей
        """

        if self.access_token != None:
            base_headers = {'authorization': 'Bearer ' + self.access_token}
            headers = base_headers if headers == None else dict(**headers, **base_headers)

        print(self.base_url)
        print(path)

        response = requester(f"{self.base_url}/{path}", params=params, json=json, headers=headers)

        if response.status_code < 200 or response.status_code > 204:
            raise AmoException(response.json())

        if response.status_code == 401 and self.refresh_token:
            raise AmoException(response.json())

        return response.json()

    def _auth(self, code: str, refresh: bool = True):
        """
        Обмен кода авторизации на ключи

        :param code: Код для получения ключей
        :param refresh: Ключ обозначающий что это обновление

        :return dict
        """
        json_params = {
            'client_id': self.integration_id,
            'client_secret': self.secret_key,
            'grant_type': 'refresh_token' if refresh else 'authorization_code',
            'redirect_uri': self.redirect_url,
        }

        if refresh:
            json_params['refresh_token'] = code
        else:
            json_params['code'] = code

        response = self._requesting('oauth2/access_token', requests.post, json_params)
        response = response['_embedded'] if '_embedded' in response else response

        if not 'access_token' in response or not 'refresh_token' in response:
            raise AmoException(response)

        self.access_token = response['access_token']
        self.refresh_token = response['refresh_token']

        return response
