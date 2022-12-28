import csv
import re
import openpyxl
from openpyxl.styles import Border, Side, NamedStyle, Font
import numpy as np
import matplotlib.pyplot as plt
import pdfkit
from jinja2 import Template
from jinja2 import Environment, FileSystemLoader

HEAD = ['name', 'salary_from', 'salary_to', 'salary_currency', 'area_name', 'published_at']
YEARS_NULL_DICT = {2007: 0, 2008: 0, 2009: 0, 2010: 0, 2011: 0, 2012: 0, 2013: 0, 2014: 0, 2015: 0, 2016: 0, 2017: 0,
                   2018: 0, 2019: 0, 2020: 0, 2021: 0, 2022: 0}
CURRENCY_TO_RUB = {"AZN": 35.68, "BYR": 23.91, "EUR": 59.90, "GEL": 21.74, "KGS": 0.76, "KZT": 0.13, "RUR": 1,
                   "UAH": 1.64, "USD": 60.66, "UZS": 0.0055}


def clean_int_point(number):
    if '.0' in number:
        number = number[:-2]
    return number


def calculate_salary_rating(vacancies):
    if len(vacancies) == 0:
        return 0
    medium_salary = 0
    for vacancy in vacancies:
        coef = CURRENCY_TO_RUB[vacancy.salary_currency]
        medium_salary += (int(clean_int_point(vacancy.salary_from)) + int(
            clean_int_point(vacancy.salary_to))) * coef // 2
    return medium_salary // len(vacancies)


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
        # coll_number = len(HEAD)
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
