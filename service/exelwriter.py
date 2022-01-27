import pandas as pd


class ExelWriter:

    id_list = []
    status_list = []
    data_list = []
    applicant_list = []
    representative_list = []
    address_list = []
    phone_list = []
    fax_list = []
    email_list = []

    def generate_data(self, data: list) -> dict:
        for dict in data:
            self.id_list.append(dict['id'])
            self.status_list.append(dict['status'])
            self.data_list.append(dict['data'])
            self.applicant_list.append(dict['applicant'])
            self.representative_list.append(dict['representative'])
            self.address_list.append(dict['address'])
            self.phone_list.append(dict['phone'])
            self.fax_list.append(dict['fax'])
            self.email_list.append(dict['email'])

        return  {
    'Номер заявки': self.id_list,
    'Состояние делопроизводства': self.status_list,
    'Дата последнего изменения': self.data_list,
    'Заявитель': self.applicant_list,
    'Патентный поверенный': self.representative_list,
    'Адрес': self.address_list,
    'Телефон': self.phone_list,
    'Факс': self.fax_list,
    'E-mail': self.email_list
}

    def write_to_exel(self, data: dict):
        data_file = pd.DataFrame(data)
        data_file.to_excel(f'output_data.xlsx', index=False)
        self._set_default()
        
    def _set_default(self):
        self.id_list = []
        self.status_list = []
        self.data_list = []
        self.applicant_list = []
        self.representative_list = []
        self.address_list = []
        self.phone_list = []
        self.fax_list = []
        self.email_list = []