class City(object):
    """класс для представления города
    Attributes:
        name (str): название
        medium_salary (int): средняя зп по городу
        vacancies ([]): список вакансий
        part (float): доля вакансий этого города ко всем вакансиям
    """

    def __init__(self, name):
        """инициализирует объект типа City
        Args:
            name(str): название
        """
        self.name = name
        self.medium_salary = 0
        self.vacancies = []
        self.part = 0
