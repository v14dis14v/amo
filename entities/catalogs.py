from entities._amo_abstract_entity import AmoAbstract


class Catalogs(AmoAbstract):
    def add(self):
        pass

    def add_element(self, catalog_id: int, name: str, custom_fields_values: dict = None) -> int:
        """
        Добавление элемента Каталога
        :param catalog_id:
        :param name:
        :param custom_fields_values:
        :return:
        """
        json = {'name': name}

        if custom_fields_values != None:
            json['custom_fields_values'] = self._map_custom_fields(custom_fields_values)

        response = self.add_elements(catalog_id, [json])

        return response[0]['id']

    def add_elements(self, catalog_id: int, data: list) -> dict:
        """
        Добавление элементов Каталога
        :param catalog_id:
        :param data:
        :return:
        """
        response = self._some_entity_request(add_url=f'{str(catalog_id)}/elements',
                                             method=self._method_post,
                                             params=data)


        return self._prepare_response(response, 'elements')

    def set(self):
        pass

    def get_elements(self, id: int, query: str = None, filter: dict = None) -> dict:
        """
        Запрос Элементов каталога

        :param id: Id Контакта
        :param company_with: Данный параметр принимает строку, в том числе из нескольких значений, указанных через запятую.

        :return: dict
        """
        params = {'page': 1, 'limit': 250}
        results = []

        if query != None:
            params['query'] = query
        if filter != None:
            params['filter'] = filter

        while True:
            response = self._some_entity_request(add_url=f'{str(id)}/elements', method=self._method_get, params=params)
            if 'elements' in response:
                results.extend(response['elements'])
                params['page'] += 1
            else:
                break

            if len(response) < params['limit']:
                break

        return results

    def delete(self):
        pass
