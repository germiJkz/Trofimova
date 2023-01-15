class Vacancy(object):
    """Класс представляет вакансию
    Attributes:
        name (str): название
        skills (str): навыки
        salary_from (str): нижняя граница зп
        salary_to (str): верхняя граница зп
        salary_currency (str): валюта
        area_name (str): название компании
        published_at (str): дата публикации
    """

    def __init__(self, vac_dict):
        """Инициализирует объект типа Vacancy

        Args:
            vac_dict (dict): словарь, хранящий сведения о вакансии
        """
        self.name = vac_dict['name']
        self.skills = list(vac_dict['key_skills'].replace('\"', '').split(', '))
        self.salary_from = vac_dict['salary_from']
        self.salary_to = vac_dict['salary_to']
        self.salary_currency = vac_dict['salary_currency']
        self.area_name = vac_dict['area_name']
        self.published_at = vac_dict['published_at']
