from amo_abstract_entity import AmoAbstract

class Leads(AmoAbstract):
    def add(self):
        pass

    def set(self):
        pass

    def get(self, id: int, lead_with: list = None):
        """
        Запрос 1 сделки по её id

        :param id: Id Сделки
        :param lead_with: Данный параметр принимает строку, в том числе из нескольких значений, указанных через запятую.

        :return:
        """
        params = None

        if lead_with != None:
            params = {'with': ','.join(lead_with)}
        response = self._requesting(f'/api/v4/leads/{str(id)}', self.method_get, params=params)

        return response['_embedded'] if '_embedded' in response else response

    def getList(self):
        pass

    def delete(self):
        pass
