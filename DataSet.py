import re
from utils import clean_int_point, calculate_salary_rating, get_skills_dict
from consts import YEARS_NULL_DICT
from Vacancy import Vacancy
from Year import Year
from City import City


class DataSet(object):

    def __init__(self, file_name, vac_name):
        """инициализирует объект датасет

        Args:
            file_name (str): имя csv-файла с данными о вакансиях
            vac_name (str): название профессии, для которой будет отдельная статистика
        """
        self.file_name = file_name
        list_vac_dict = self.csv_parser(file_name)

        if not list_vac_dict:
            self.vacancies_objects = []
        else:
            self.vacancies_objects = [Vacancy(vac_dict) for vac_dict in list_vac_dict]
        self.vacancies_objects_param = [vacancy for vacancy in self.vacancies_objects if
                                        'python'.lower() in vacancy.name.lower() or
                                        'питон'.lower() in vacancy.name.lower() or
                                        'пайтон'.lower() in vacancy.name.lower()]

        self.skills_dict = get_skills_dict(self.vacancies_objects)
        self.skills_dict_param = get_skills_dict(self.vacancies_objects_param)

        self.years_list, self.cities_list = self.collect_years(vac_name)
        for year in self.years_list:
            year.salary_rating = calculate_salary_rating(year.vacancies)
            year.param_salary_rating = calculate_salary_rating(year.param_vacancies)
        count_vac = len(self.vacancies_objects)
        low_line = count_vac // 100
        for city in self.cities_list:
            count_vac_by_city = len(city.vacancies)
            if count_vac_by_city > low_line:
                city.part = count_vac_by_city / count_vac
                city.medium_salary = calculate_salary_rating(city.vacancies)

        self.cities_sort_by_salary = sorted(self.cities_list, key=lambda city: city.medium_salary, reverse=True)
        self.cities_sort_by_part = sorted(self.cities_list, key=lambda city: city.part, reverse=True)
        self.best_skill = max(self.skills_dict, key=self.skills_dict.get)
        self.best_skill_score = self.skills_dict[self.best_skill]
        self.best_skill_param = max(self.skills_dict_param, key=self.skills_dict_param.get)
        self.best_skill_score_param = self.skills_dict_param[self.best_skill_param]

    def csv_parser(self, file_name):
        """Читает файл, записывает данные в список словарей

        Args:
            file_name: имя csv-файла с данными о вакансиях
        Returns:
            [dict]: список словарей, где каждый словарь хранит в себе данные о вакансиях
        """
        is_head = True
        list_vac_dict = []
        with open(file_name, encoding='utf-8-sig') as f:
            for row in f.readlines():
                row = row.replace(', ', '##')
                if row.count(',') == 6:
                    row = row.split(',')
                    row = [item.replace('##', ', ') for item in row]
                    row = list(filter(None, row))

                    if is_head:
                        is_head = False
                        head = row
                        for i in range(len(head)):
                            head[i] = head[i].replace(';', '').replace('\n', '')
                    elif len(head) == len(row) and clean_int_point(row[2]).isdigit() and clean_int_point(
                            row[3]).isdigit():
                        vacancy_dict = dict.fromkeys(head)
                        for i in range(len(head)):
                            key = head[i]
                            value = " ".join(re.sub(re.compile('<.*?>'), '', row[i]).replace('\n', '###')
                                             .replace('\r\n', '').split())
                            if key == 'published_at':
                                vacancy_dict[key] = value.replace(';', '').replace('###', '')
                            else:
                                vacancy_dict[key] = value
                        list_vac_dict.append(vacancy_dict)

        return list_vac_dict

    def collect_years(self, vac_name):
        """Распределяет вакансии по годам и городам

        Args:
            vac_name: имя csv-файла с данными о вакансиях
        Returns:
            [Year]: список годов
            [City]: список городов
        """
        years_list = [Year(number) for number in range(2015, 2023)]
        cities_list = []
        city_names = []

        for vacancy in self.vacancies_objects:
            vac_year = int(vacancy.published_at[:4])

            years_list[vac_year - 2015].vacancies.append(vacancy)
            for skill in vacancy.skills:
                if skill not in years_list[vac_year - 2015].skills.keys():
                    years_list[vac_year - 2015].skills.update({skill: 1})
                else:
                    years_list[vac_year - 2015].skills[skill] += 1

            if vacancy.area_name not in city_names:
                city_names.append(vacancy.area_name)
                cities_list.append(City(vacancy.area_name))
            cities_list[city_names.index(vacancy.area_name)].vacancies.append(vacancy)

        for vacancy in self.vacancies_objects_param:
            vac_year = int(vacancy.published_at[:4])

            years_list[vac_year - 2015].param_vacancies.append(vacancy)
            for skill in vacancy.skills:
                if skill not in years_list[vac_year - 2015].skills_param.keys():
                    years_list[vac_year - 2015].skills_param.update({skill: 1})
                else:
                    years_list[vac_year - 2015].skills_param[skill] += 1

        return years_list, cities_list
