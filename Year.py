class Year(object):
    """класс для представления года
    Attributes:
        number (int): номер
        vacancies ([]): список вакансий
        param_vacancies ([]): список вакансий определённой профессии
        salary_rating (int): средняя зп
        param_salary_rating (int): средняя зп для определённой профессии
    """

    def __init__(self, number):
        """инициализирует объект типа Year
        Args:
            number(int): номер года
        """
        self.number = number
        self.vacancies = []
        self.param_vacancies = []
        self.salary_rating = 0
        self.param_salary_rating = 0
