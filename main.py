import csv
import re
import openpyxl
from openpyxl.styles import Border, Side, NamedStyle, Font
import numpy as np
import matplotlib.pyplot as plt
import pdfkit
from jinja2 import Template
from jinja2 import Environment, FileSystemLoader
from var_dump import var_dump
from prettytable import PrettyTable
from prettytable import ALL

SHORT_HEAD = ['name', 'salary_from', 'salary_to', 'salary_currency', 'area_name', 'published_at']
YEARS_NULL_DICT = {2007: 0, 2008: 0, 2009: 0, 2010: 0, 2011: 0, 2012: 0, 2013: 0, 2014: 0, 2015: 0, 2016: 0, 2017: 0,
                   2018: 0, 2019: 0, 2020: 0, 2021: 0, 2022: 0}
CURRENCY_TO_RUB = {"AZN": 35.68, "BYR": 23.91, "EUR": 59.90, "GEL": 21.74, "KGS": 0.76, "KZT": 0.13, "RUR": 1,
                   "UAH": 1.64, "USD": 60.66, "UZS": 0.0055}
HEAD = ['name', 'description', 'key_skills', 'experience_id', 'premium', 'employer_name', 'salary_from',
        'salary_to', 'salary_gross', 'salary_currency', 'area_name', 'published_at']
RUS_HEAD = ['Оклад', 'Название', 'Описание', 'Навыки', 'Опыт работы', 'Премиум-вакансия', 'Компания',
            'Нижний порог оклада', 'Верхний порог оклада', 'С учётом налогов', 'Идентификатор валюты оклада',
            'Название региона', 'Дата публикации вакансии']
RUS_HEAD_FOR_PRINT = ['№', 'Название', 'Описание', 'Навыки', 'Опыт работы', 'Премиум-вакансия', 'Компания', 'Оклад',
                      'Название региона', 'Дата публикации вакансии']
WORK_EXPERIENCE = {"noExperience": "Нет опыта", "between1And3": "От 1 года до 3 лет",
                   "between3And6": "От 3 до 6 лет", "moreThan6": "Более 6 лет"}
WORK_EXPERIENCE_BACK = {"Нет опыта": "noExperience", "От 1 года до 3 лет": "between1And3",
                        "От 3 до 6 лет": "between3And6", "Более 6 лет": "moreThan6"}
WORK_EXPERIENCE_FOR_SORT = {"noExperience": "а", "Нет опыта": "а", "between1And3": "б", "От 1 года до 3 лет": "б",
                            "between3And6": "в", "От 3 до 6 лет": "в", "moreThan6": "г", "Более 6 лет": "г"}
BOOL_TRANSLATE = {'TRUE': 'Да', 'True': 'Да', 'FALSE': 'Нет', 'False': 'Нет'}
BOOL_TRANSLATE_BACK = {'Да': 'TRUE', 'Нет': 'FALSE'}
CURRENCY = {"AZN": "Манаты", "BYR": "Белорусские рубли", "EUR": "Евро", "GEL": "Грузинский лари",
            "KGS": "Киргизский сом", "KZT": "Тенге", "RUR": "Рубли", "UAH": "Гривны", "USD": "Доллары",
            "UZS": "Узбекский сум"}
CURRENCY_BACK = {"Манаты": "AZN", "Белорусские рубли": "BYR", "Евро": "EUR", "Грузинский лари": "GEL",
                 "Киргизский сом": "KGS", "Тенге": "KZT", "Рубли": "RUR", "Гривны": "UAH", "Доллары": "USD",
                 "Узбекский сум": "UZS"}


def clean_int_point(number):
    if '.0' in number:
        number = number[:-2]
    return number


def clean_int(number):
    if '.0' in number:
        number = number[:-2]
    if len(number) > 3 and number[-4] != ' ':
        number = number[:-3] + ' ' + number[-3:]
    return number


def convert_data(string):
    day = string[8:10]
    month = string[5:7]
    year = string[:4]
    return day + '.' + month + '.' + year


def calculate_salary_rating(vacancies):
    if len(vacancies) == 0:
        return 0
    medium_salary = 0
    for vacancy in vacancies:
        coef = CURRENCY_TO_RUB[vacancy.salary_currency]
        medium_salary += (int(clean_int_point(vacancy.salary_from)) + int(
            clean_int_point(vacancy.salary_to))) * coef // 2
    return medium_salary // len(vacancies)


class DataSetForTable(object):

    def __init__(self, file_name):
        list_vac_dict = self.csv_parser(file_name)

        self.file_name = file_name
        if not list_vac_dict:
            self.vacancies_objects = []
        else:
            self.vacancies_objects = [VacancyForTable(vac_dict) for vac_dict in list_vac_dict]

    def csv_parser(self, file_name):
        is_head = True
        rows = []
        with open(file_name, encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            for row in reader:
                row = list(filter(None, row))
                if is_head:
                    is_head = False
                    head = row
                    coll_number = len(head)
                elif coll_number == len(row):
                    rows.append(row)
        list_vac_dict = []
        for row in rows:
            vacancy_dict = dict.fromkeys(HEAD)
            for i in range(len(HEAD)):
                key = HEAD[i]
                value = " ".join(re.sub(re.compile('<.*?>'), '', row[i]).replace('\n', '###')
                                 .replace('\r\n', '').split())
                vacancy_dict[key] = value
            list_vac_dict.append(vacancy_dict)
        return list_vac_dict

    def filter(self, filter_param):
        filtered_vacancy = []
        index = filter_param.index(':')
        param_name = filter_param[:index]
        param_value = filter_param[index + 2:]
        if param_name == 'Название':
            for vacancy in self.vacancies_objects:
                if vacancy.name == param_value:
                    filtered_vacancy.append(vacancy)
        elif param_name == 'Описание':
            for vacancy in self.vacancies_objects:
                if vacancy.description == param_value:
                    filtered_vacancy.append(vacancy)
        elif param_name == 'Компания':
            for vacancy in self.vacancies_objects:
                if vacancy.employer_name == param_value:
                    filtered_vacancy.append(vacancy)
        elif param_name == 'Название региона':
            for vacancy in self.vacancies_objects:
                if vacancy.area_name == param_value:
                    filtered_vacancy.append(vacancy)
        elif param_name == 'Опыт работы':
            for vacancy in self.vacancies_objects:
                if vacancy.experience_id == WORK_EXPERIENCE_BACK[param_value]:
                    filtered_vacancy.append(vacancy)
        elif param_name == 'Премиум-вакансия':
            for vacancy in self.vacancies_objects:
                if vacancy.premium.lower() == BOOL_TRANSLATE_BACK[param_value].lower():
                    filtered_vacancy.append(vacancy)
        elif param_name == 'Идентификатор валюты оклада':
            for vacancy in self.vacancies_objects:
                if vacancy.salary.salary_currency == CURRENCY_BACK[param_value]:
                    filtered_vacancy.append(vacancy)
        elif param_name == 'Оклад':
            for vacancy in self.vacancies_objects:
                if int(vacancy.salary.salary_from) <= int(param_value) <= int(vacancy.salary.salary_to):
                    filtered_vacancy.append(vacancy)
        elif param_name == 'Дата публикации вакансии':
            for vacancy in self.vacancies_objects:
                data = convert_data(vacancy.published_at)
                if data == param_value:
                    filtered_vacancy.append(vacancy)
        elif param_name == 'Навыки':
            for vacancy in self.vacancies_objects:
                need_skills = param_value.split(', ')
                counter = 0
                for n_skill in need_skills:
                    if n_skill in vacancy.key_skills:
                        counter += 1
                if counter == len(need_skills):
                    filtered_vacancy.append(vacancy)

        self.vacancies_objects = filtered_vacancy

    def translate(self):
        for vacancy in self.vacancies_objects:
            vacancy.experience_id = WORK_EXPERIENCE[vacancy.experience_id]
            vacancy.premium = BOOL_TRANSLATE[vacancy.premium]
            vacancy.salary.salary_gross = BOOL_TRANSLATE[vacancy.salary.salary_gross]

            year = vacancy.published_at[:4]
            month = vacancy.published_at[5:7]
            day = vacancy.published_at[8:10]
            hour = vacancy.published_at[11:13]
            min = vacancy.published_at[14:16]
            sec = vacancy.published_at[17:19]
            vacancy.published_at = year + '.' + month + '.' + day + ' ' + hour + ':' + min + ':' + sec

    def sort(self, sort_param, is_reverse_sort):
        if sort_param == 'Название':
            self.vacancies_objects = sorted(self.vacancies_objects, key=lambda vac: vac.name, reverse=is_reverse_sort)
        elif sort_param == 'Описание':
            self.vacancies_objects = sorted(self.vacancies_objects, key=lambda vac: vac.description,
                                            reverse=is_reverse_sort)
        elif sort_param == 'Компания':
            self.vacancies_objects = sorted(self.vacancies_objects, key=lambda vac: vac.employer_name,
                                            reverse=is_reverse_sort)
        elif sort_param == 'Название региона':
            self.vacancies_objects = sorted(self.vacancies_objects, key=lambda vac: vac.area_name,
                                            reverse=is_reverse_sort)
        elif sort_param == 'Премиум-вакансия':
            self.vacancies_objects = sorted(self.vacancies_objects, key=lambda vac: vac.premium,
                                            reverse=is_reverse_sort)
        elif sort_param == 'Опыт работы':
            self.vacancies_objects = sorted(self.vacancies_objects,
                                            key=lambda vac: WORK_EXPERIENCE_FOR_SORT[vac.experience_id],
                                            reverse=is_reverse_sort)
        elif sort_param == 'Навыки':
            self.vacancies_objects = sorted(self.vacancies_objects, key=lambda vac: len(vac.key_skills),
                                            reverse=is_reverse_sort)
        elif sort_param == 'Оклад':
            self.vacancies_objects = sorted(self.vacancies_objects, key=lambda vac: vac.salary.get_convert_salary(),
                                            reverse=is_reverse_sort)
        elif sort_param == 'Дата публикации вакансии':
            self.vacancies_objects = sorted(self.vacancies_objects, key=lambda vac: vac.published_at,
                                            reverse=is_reverse_sort)

    def print_table(self, lines_to_print, colomns):
        table = PrettyTable()
        table._max_width = {'№': 20, 'Название': 20, 'Описание': 20, 'Навыки': 20, 'Опыт работы': 20,
                            'Премиум-вакансия': 20, 'Компания': 20, 'Оклад': 20, 'Название региона': 20,
                            'Дата публикации вакансии': 20}
        table.hrules = ALL
        table.align = 'l'
        table.field_names = RUS_HEAD_FOR_PRINT
        for i in range(len(self.vacancies_objects)):
            vacancy = self.vacancies_objects[i]
            row = [str(i + 1), vacancy.name, vacancy.description, '\n'.join(vacancy.key_skills), vacancy.experience_id,
                   vacancy.premium, vacancy.employer_name, vacancy.salary.string_for_table, vacancy.area_name,
                   convert_data(vacancy.published_at)]
            for j in range(len(row)):
                item = row[j]
                if len(item) > 100:
                    row[j] = item[:100] + '...'
            table.add_row(row)

        if colomns == '':
            colomns = table.field_names
        else:
            colomns = colomns.split(', ')
            colomns.insert(0, '№')
        if lines_to_print == '':
            table = table.get_string(fields=colomns)
        elif ' ' in lines_to_print:
            lines_to_print = lines_to_print.split(' ')
            table = table.get_string(start=int(lines_to_print[0]) - 1, end=int(lines_to_print[1]) - 1, fields=colomns)
        else:
            table = table.get_string(start=int(lines_to_print) - 1, fields=colomns)

        print(table)


class VacancyForTable(object):

    def __init__(self, vac_dict):
        self.name = vac_dict['name']
        self.description = vac_dict['description']
        self.key_skills = vac_dict['key_skills'].split('###')
        self.experience_id = vac_dict['experience_id']
        self.premium = vac_dict['premium']
        self.employer_name = vac_dict['employer_name']
        self.salary = SalaryForTable(vac_dict['salary_from'], vac_dict['salary_to'], vac_dict['salary_gross'],
                                     vac_dict['salary_currency'])
        self.area_name = vac_dict['area_name']
        self.published_at = vac_dict['published_at']


class SalaryForTable(object):

    def __init__(self, salary_from, salary_to, salary_gross, salary_currency):
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.salary_gross = salary_gross
        self.salary_currency = salary_currency
        self.string_for_table = self.get_string_for_table()

    def get_convert_salary(self):
        currency_to_rub = {"AZN": 35.68, "BYR": 23.91, "EUR": 59.90, "GEL": 21.74, "KGS": 0.76, "KZT": 0.13, "RUR": 1,
                           "UAH": 1.64, "USD": 60.66, "UZS": 0.0055}
        coef = currency_to_rub[self.salary_currency]
        return (int(clean_int_point(self.salary_from)) * coef + int(clean_int_point(self.salary_to)) * coef) // 2

    def get_string_for_table(self):
        salary = clean_int(self.salary_from) + ' - ' + clean_int(self.salary_to) + ' (' + CURRENCY[
            self.salary_currency] + ') ('
        if self.salary_gross == 'Да' or self.salary_gross == 'True' or self.salary_gross == 'TRUE':
            salary += 'Без вычета налогов)'
        else:
            salary += 'С вычетом налогов)'
        return salary


class DataSet(object):

    def __init__(self, file_name, vac_name):
        list_vac_dict = self.csv_parser(file_name)

        self.file_name = file_name
        if not list_vac_dict:
            self.vacancies_objects = []
        else:
            self.vacancies_objects = [Vacancy(vac_dict) for vac_dict in list_vac_dict]

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

    def csv_parser(self, file_name):
        is_head = True
        # coll_number = len(SHORT_HEAD)
        list_vac_dict = []
        with open(file_name, encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            for row in reader:
                row = list(filter(None, row))
                if is_head:
                    is_head = False
                    head = row
                elif len(head) == len(row):
                    vacancy_dict = dict.fromkeys(head)
                    for i in range(len(head)):
                        key = head[i]
                        value = " ".join(re.sub(re.compile('<.*?>'), '', row[i]).replace('\n', '###')
                                         .replace('\r\n', '').split())
                        vacancy_dict[key] = value
                    list_vac_dict.append(vacancy_dict)

        return list_vac_dict

    def collect_years(self, vac_name):
        years_list = [Year(number) for number in range(2007, 2023)]
        cities_list = []
        city_names = []
        for vacancy in self.vacancies_objects:
            vac_year = int(vacancy.published_at[:4])
            years_list[vac_year - 2007].vacancies.append(vacancy)
            if vac_name in vacancy.name:
                years_list[vac_year - 2007].param_vacancies.append(vacancy)
            if vacancy.area_name not in city_names:
                city_names.append(vacancy.area_name)
                cities_list.append(City(vacancy.area_name))
            cities_list[city_names.index(vacancy.area_name)].vacancies.append(vacancy)

        return years_list, cities_list


class Vacancy(object):

    def __init__(self, vac_dict):
        self.name = vac_dict['name']
        self.salary_from = vac_dict['salary_from']
        self.salary_to = vac_dict['salary_to']
        self.salary_currency = vac_dict['salary_currency']
        self.area_name = vac_dict['area_name']
        self.published_at = vac_dict['published_at']


class Year(object):

    def __init__(self, number):
        self.number = number
        self.vacancies = []
        self.param_vacancies = []
        self.salary_rating = 0
        self.param_salary_rating = 0


class City(object):

    def __init__(self, name):
        self.name = name
        self.medium_salary = 0
        self.vacancies = []
        self.part = 0


class InputConect(object):

    def __init__(self, file_name, filter_param, sort_param, reverse_sort):
        num_lines = sum(1 for line in open(file_name, encoding='utf-8-sig'))
        self.is_empty = num_lines == 0
        self.is_no_data = num_lines == 1
        self.is_pos_filter = filter_param != ''
        self.filter_param = filter_param
        self.is_pos_sort = sort_param != ''
        self.sort_param = sort_param
        self.is_reverse_sort = reverse_sort == 'Да'
        self.reverse_sort = reverse_sort
        self.is_printable = self.chek_errors()

    def chek_errors(self):
        is_printable = True
        if self.is_empty:
            print('Пустой файл')
            is_printable = False
        if self.is_no_data:
            print('Нет данных')
            is_printable = False
        if ': ' not in self.filter_param and self.filter_param != '':
            print('Формат ввода некорректен')
            is_printable = False
        elif self.filter_param != '':
            if self.filter_param[:self.filter_param.index(':')] not in RUS_HEAD:
                print('Параметр поиска некорректен')
                is_printable = False

        if self.sort_param not in RUS_HEAD and self.sort_param != '':
            is_printable = False
            print('Параметр сортировки некорректен')

        if self.reverse_sort != 'Да' and self.reverse_sort != 'Нет' and self.reverse_sort != '':
            print('Порядок сортировки задан некорректно')
            is_printable = False

        return is_printable


class Report(object):

    def __init__(self, data_set, vac_name):
        self.data_set = data_set
        self.salary_by_year = {year.number: int(clean_int_point(str(year.salary_rating))) for year in
                               data_set.years_list if year.salary_rating != 0}
        self.count_salary_by_year = {year.number: len(year.vacancies) for year in data_set.years_list if
                                     len(year.vacancies) != 0}
        self.salary_by_year_by_vacancy = {year.number: year.param_salary_rating for year in data_set.years_list if
                                          year.param_salary_rating != 0}
        self.count_salary_by_year_by_vacancy = {year.number: len(year.param_vacancies) for year in data_set.years_list
                                                if len(year.param_vacancies) != 0}
        self.salary_by_city = {city.name: int(clean_int_point(str(city.medium_salary))) for city in
                               data_set.cities_sort_by_salary[:10] if city.medium_salary != 0}
        self.part_salary_by_city = {city.name: round(city.part, 4) for city in data_set.cities_sort_by_part[:10] if
                                    round(city.part, 4) != 0}
        self.procent_salary_by_city = [str(int(n * 10000) / 100) + '%' for n in self.part_salary_by_city.values()]
        self.vac_name = vac_name

    def generate_excel(self):
        book = openpyxl.Workbook()
        sheet1 = book.active
        sheet1.title = 'Статистика по годам'
        sheet1['A1'] = 'Год'
        sheet1['B1'] = 'Средняя зарплата '
        sheet1['C1'] = 'Средняя зарплата - ' + self.vac_name
        sheet1['D1'] = 'Количество вакансий '
        sheet1['E1'] = 'Количество вакансий - ' + self.vac_name
        sheet1.column_dimensions['A'].width = 5
        sheet1.column_dimensions['B'].width = len(sheet1['B1'].value)
        sheet1.column_dimensions['C'].width = len(sheet1['C1'].value)
        sheet1.column_dimensions['D'].width = len(sheet1['D1'].value)
        sheet1.column_dimensions['E'].width = len(sheet1['E1'].value)

        thin_side = Side(border_style='thin')
        thin_borders = Border(top=thin_side, left=thin_side, right=thin_side, bottom=thin_side)

        text_style = NamedStyle(name="text_style")
        text_style.border = thin_borders

        topic_style = NamedStyle(name="topic_style")
        topic_style.font = Font(bold=True)
        topic_style.border = thin_borders

        sheet1['A1'].style = topic_style
        sheet1['B1'].style = topic_style
        sheet1['C1'].style = topic_style
        sheet1['D1'].style = topic_style
        sheet1['E1'].style = topic_style

        years = list(YEARS_NULL_DICT.keys())
        for i in range(2, 18):
            sheet1['A' + str(i)] = years[i - 2]
            sheet1['A' + str(i)].style = text_style

        for i in range(2, 18):
            sheet1['B' + str(i)] = self.salary_by_year[i - 2 + 2007]
            sheet1['B' + str(i)].style = text_style

        for i in range(2, 18):
            sheet1['C' + str(i)] = self.salary_by_year_by_vacancy[i - 2 + 2007]
            sheet1['C' + str(i)].style = text_style

        for i in range(2, 18):
            sheet1['D' + str(i)] = self.count_salary_by_year[i - 2 + 2007]
            sheet1['D' + str(i)].style = text_style

        for i in range(2, 18):
            sheet1['E' + str(i)] = self.count_salary_by_year_by_vacancy[i - 2 + 2007]
            sheet1['E' + str(i)].style = text_style

        sheet2 = book.create_sheet('Статистика по городам')
        sheet2['A1'] = 'Город '
        sheet2['B1'] = 'Уровень зарплат '
        sheet2['D1'] = 'Город '
        sheet2['E1'] = 'Доля вакансий '
        sheet2.column_dimensions['A'].width = max(max([len(n) for n in self.salary_by_city.keys()]) + 1, 7)
        sheet2.column_dimensions['B'].width = len(sheet2['B1'].value)
        sheet2.column_dimensions['C'].width = 2
        sheet2.column_dimensions['D'].width = max(max([len(n) for n in self.part_salary_by_city.keys()]) + 1, 7)
        sheet2.column_dimensions['E'].width = len(sheet2['E1'].value)
        sheet2['A1'].style = topic_style
        sheet2['B1'].style = topic_style
        sheet2['D1'].style = topic_style
        sheet2['E1'].style = topic_style

        cities_salaries = list(self.salary_by_city.keys())
        for i in range(2, 12):
            sheet2['A' + str(i)] = cities_salaries[i - 2]
            sheet2['A' + str(i)].style = text_style
        for i in range(2, 12):
            sheet2['B' + str(i)] = self.salary_by_city[cities_salaries[i - 2]]
            sheet2['B' + str(i)].style = text_style

        cities_part = list(self.part_salary_by_city.keys())
        for i in range(2, 12):
            sheet2['D' + str(i)] = cities_part[i - 2]
            sheet2['D' + str(i)].style = text_style
        for i in range(2, 12):
            sheet2['E' + str(i)] = self.part_salary_by_city[cities_part[i - 2]]
            sheet2['E' + str(i)].style = text_style
            sheet2['E' + str(i)].number_format = '0.00%'

        book.save("report.xlsx")

    def generate_image(self):

        yearsX = list(self.salary_by_year.keys())
        years1 = [n - 0.2 for n in yearsX]
        years2 = [n + 0.2 for n in yearsX]

        fig, axes = plt.subplots(2, 2)

        axes[0][0].set_title('Уровень зарплат по годам', {'fontsize': 8})
        axes[0][0].set_xticks(yearsX)
        axes[0][0].tick_params(axis='x', rotation=90, labelsize=8)
        axes[0][0].tick_params(axis='y', labelsize=8)
        axes[0][0].bar(years1, list(self.salary_by_year.values()), label='средняя з/п', width=0.4)
        axes[0][0].bar(years2, list(self.salary_by_year_by_vacancy.values()),
                       label='з/п ' + str(self.vac_name), width=0.4)
        axes[0][0].grid(axis='y')
        axes[0][0].legend(fontsize=8)

        axes[0][1].set_title('Количество вакансий по годам', {'fontsize': 8})
        axes[0][1].set_xticks(yearsX)
        axes[0][1].tick_params(axis='x', rotation=90, labelsize=8)
        axes[0][1].tick_params(axis='y', labelsize=8)
        axes[0][1].bar(years1, list(self.count_salary_by_year.values()), label='количество вакансий ', width=0.4)
        axes[0][1].bar(years2, list(self.count_salary_by_year_by_vacancy.values()),
                       label='количество вакансий ' + str(self.vac_name),
                       width=0.4)
        axes[0][1].grid(axis='y')
        axes[0][1].legend(fontsize=8)

        axes[1][0].barh(range(10), list(reversed(list(self.salary_by_city.values()))),
                        tick_label=list(reversed(list(self.salary_by_city.keys()))))
        axes[1][0].grid(axis='x')
        axes[1][0].set_title('Уровень зарплат по городам', {'fontsize': 6})
        axes[1][0].tick_params(axis='both', labelsize=6)

        self.part_salary_by_city.update({'Другие': 1 - sum(list(self.part_salary_by_city.values()))})
        axes[1][1].pie(list(self.part_salary_by_city.values()), labels=list(self.part_salary_by_city.keys()),
                       textprops={'fontsize': 6})
        axes[1][1].set_title('Доля вакансий по городам', {'fontsize': 6})

        fig.tight_layout()
        plt.savefig('graph.png')

    def generate_pdf(self, image_name):
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template("template.html")

        pdf_template = template.render({'vac_name': self.vac_name,
                                        'image_file': image_name,
                                        'years': list(YEARS_NULL_DICT.keys()),
                                        'salary_by_year': self.salary_by_year,
                                        'count_salary_by_year': self.count_salary_by_year,
                                        'salary_by_year_by_vacancy': self.salary_by_year_by_vacancy,
                                        'count_salary_by_year_by_vacancy': self.count_salary_by_year_by_vacancy,
                                        'cities_salaries': list(self.salary_by_city.keys()),
                                        'salary_by_city': self.salary_by_city,
                                        'cities_part': list(self.part_salary_by_city.keys()),
                                        'part_salary_by_city': self.procent_salary_by_city
                                        })

        config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
        options = {'enable-local-file-access': None}
        pdfkit.from_string(pdf_template, 'report.pdf', configuration=config, options=options)

example = 2 #провокатор
workMode = input('Вакансии или статистика?(укажите одно из двух): ')
if workMode.lower() == 'вакансии':
    file_name = 'vacancies (2).csv'  # input('Введите название файла: ')
    filter_param = ''  # input('Введите параметр фильтрации: ')
    sort_param = 'Оклад'  # input('Введите параметр сортировки: ')
    reverse_sort = 'Да'  # input('Обратный порядок сортировки (Да / Нет): ')
    lines_to_print = ''  # input('Введите диапазон вывода: ')
    colomns = ''  # input('Введите требуемые столбцы: ')

    input_connect = InputConect(file_name, filter_param, sort_param, reverse_sort)
    if input_connect.is_printable:
        data_set = DataSetForTable(file_name)
        if input_connect.is_pos_filter:
            data_set.filter(input_connect.filter_param)
        if not data_set.vacancies_objects:
            print('Ничего не найдено')
        else:
            data_set.translate()
            if input_connect.is_pos_sort:
                data_set.sort(input_connect.sort_param, input_connect.is_reverse_sort)
            data_set.print_table(lines_to_print, colomns)

elif workMode.lower() == 'статистика':
    file_name = 'vacancies_by_year.csv'  # input('Введите название файла: ')
    vac_name = 'Программист'  # input('Введите название профессии: ')

    data_set = DataSet(file_name, vac_name)
    new_report = Report(data_set, vac_name)

    print(new_report.salary_by_year)
    print(new_report.salary_by_year_by_vacancy)
    print(new_report.count_salary_by_year)
    print(new_report.count_salary_by_year_by_vacancy)
    print(new_report.salary_by_city)
    print(new_report.part_salary_by_city)

    new_report.generate_excel()
    new_report.generate_image()
    new_report.generate_pdf("graph.png")
else:
    console.log('Вы ввели что-то не то')
