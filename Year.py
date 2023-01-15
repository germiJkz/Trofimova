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
        self.skills = {}
        self.skills_param = {}

    def get_max_skill(self):
        if len(self.skills) > 0:
            key = max(self.skills, key=self.skills.get)
            return {key: self.skills[key]}
        return {}

    def get_max_skill_param(self):
        if len(self.skills_param) > 0:
            key = max(self.skills_param, key=self.skills_param.get)
            return {key: self.skills_param[key]}
        return {}

