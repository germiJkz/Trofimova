import openpyxl
from openpyxl.styles import Border, Side, NamedStyle, Font
import matplotlib.pyplot as plt
import pdfkit
from jinja2 import Template
from jinja2 import Environment, FileSystemLoader
from consts import YEARS_NULL_DICT
from utils import clean_int_point


class Report(object):
    """класс для формирования отчётов
    Attributes:
        data_set (DataSet): датасет на основе котрого будут формироваться отчёты
        salary_by_year ({int: int}): словарь с данными о средней зп за каждый год
        count_salary_by_year ({int: int}): словарь с данными о кол-ве вакансий за каждый год
        salary_by_year_by_vacancy ({int: int}): словарь с данными о средней зп за каждый год для определённой професии
        count_salary_by_year_by_vacancy ({int: int}): словарь с данными о кол-ве вакансий за каждый год для
                                                    определённой професии
        salary_by_city ({str: int}): словарь с данными о средней зп о каждом городе (топ 10)
        part_salary_by_city ({str: float}): словарь с данными о доле вакансий о каждом городе (топ 10)
        procent_salary_by_city ([str]): список  с данными о доле вакансий о каждом городе (топ 10) в виде процентов
        vac_name (str): название проффесии, для которой будет отдельная статистика
    """

    def __init__(self, data_set, vac_name):
        """инициализирует объект типа Report
        Args:
            data_set (DataSet): датасет на основе котрого будут формироваться отчёты
            vac_name (str): название проффесии, для которой будет отдельная статистика
        """
        self.data_set = data_set
        self.salary_by_year = {year.number: int(clean_int_point(str(year.salary_rating))) for year in
                               data_set.years_list}  # if year.salary_rating != 0
        self.count_salary_by_year = {year.number: len(year.vacancies) for year in data_set.years_list}
        self.salary_by_year_by_vacancy = {year.number: int(clean_int_point(str(year.param_salary_rating))) for year in
                                          data_set.years_list}
        self.count_salary_by_year_by_vacancy = {year.number: len(year.param_vacancies) for year in data_set.years_list}
        self.salary_by_city = {city.name: int(clean_int_point(str(city.medium_salary))) for city in
                               data_set.cities_sort_by_salary[:10]}
        self.part_salary_by_city = {city.name: round(city.part, 4) for city in data_set.cities_sort_by_part[:10]}
        self.procent_salary_by_city = [str(int(n * 10000) / 100) + '%' for n in self.part_salary_by_city.values()]
        self.skills_by_year = {year.number: year.get_max_skill() for year in data_set.years_list}
        self.skills_by_year_param = {year.number: year.get_max_skill_param() for year in data_set.years_list}
        self.vac_name = vac_name

    def generate_excel(self):
        """Генерирует xlsx-файл со статистикой
        """
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
        for i in range(2, 9):
            sheet1['A' + str(i)] = years[i - 2]
            sheet1['A' + str(i)].style = text_style

        for i in range(2, 9):
            sheet1['B' + str(i)] = self.salary_by_year[i - 2 + 2015]
            sheet1['B' + str(i)].style = text_style

        for i in range(2, 9):
            sheet1['C' + str(i)] = self.salary_by_year_by_vacancy[i - 2 + 2015]
            sheet1['C' + str(i)].style = text_style

        for i in range(2, 9):
            sheet1['D' + str(i)] = self.count_salary_by_year[i - 2 + 2015]
            sheet1['D' + str(i)].style = text_style

        for i in range(2, 9):
            sheet1['E' + str(i)] = self.count_salary_by_year_by_vacancy[i - 2 + 2015]
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

        book.save("report/report.xlsx")

    def generate_image(self):
        """Генерирует png-файл со статистикой(диаграммы и графики)
        """
        plt.rc('font', family='Times New Roman')

        years_x = list(self.salary_by_year.keys())
        years1 = [n - 0.2 for n in years_x]
        years2 = [n + 0.2 for n in years_x]

        fig, axe = plt.subplots()
        axe.set_title('Уровень зарплат по годам', {'fontsize': 16})
        axe.set_xticks(years_x)
        axe.tick_params(axis='x', rotation=90, labelsize=10)
        axe.tick_params(axis='y', labelsize=10)
        axe.bar(years1, list(self.salary_by_year.values()), label='средняя з/п', width=0.4)
        axe.bar(years2, list(self.salary_by_year_by_vacancy.values()), label='з/п ' + str(self.vac_name), width=0.4)
        axe.grid(axis='y')
        axe.legend(fontsize=10)
        plt.savefig('report/salary_rating_by_years.png')

        fig, axe = plt.subplots()
        axe.set_title('Количество вакансий по годам', {'fontsize': 16})
        axe.set_xticks(years_x)
        axe.tick_params(axis='x', rotation=90, labelsize=10)
        axe.tick_params(axis='y', labelsize=10)
        axe.bar(years1, list(self.count_salary_by_year.values()), label='количество вакансий ', width=0.4)
        axe.bar(years2, list(self.count_salary_by_year_by_vacancy.values()), label='количество вакансий ' +
                                                                                   str(self.vac_name), width=0.4)
        axe.grid(axis='y')
        axe.legend(fontsize=10)
        plt.savefig('report/salary_count_by_years.png')

        fig, axe = plt.subplots()
        fig.set_size_inches(11, 5)
        axe.barh(range(10), list(reversed(list(self.salary_by_city.values()))),
                 tick_label=list(reversed(list(self.salary_by_city.keys()))))
        axe.grid(axis='x')
        axe.set_title('Уровень зарплат по городам', {'fontsize': 16})
        axe.tick_params(axis='both', labelsize=10)
        plt.savefig('report/salary_rating_by_cities.png')

        self.part_salary_by_city.update({'Другие': 1 - sum(list(self.part_salary_by_city.values()))})
        fig, axe = plt.subplots()
        axe.pie(list(self.part_salary_by_city.values()), labels=list(self.part_salary_by_city.keys()),
                textprops={'fontsize': 10})
        axe.set_title('Доля вакансий по городам', {'fontsize': 16})

        fig.tight_layout()
        plt.savefig('report/part_count_by_sities.png')

        skills1 = [list(self.skills_by_year[year].values())[0] for year in range(2015, 2023)]
        skills2 = [list(self.skills_by_year_param[year].values())[0] for year in range(2015, 2023)]
        labels1 = [list(self.skills_by_year[year].keys())[0] for year in range(2015, 2023)]
        labels2 = [list(self.skills_by_year_param[year].keys())[0] for year in range(2015, 2023)]
        fig, axe = plt.subplots()
        axe.set_title('Самые популярные навыки по годам', {'fontsize': 16})
        axe.set_ylabel('Количество упоминаний')
        axe.set_xticks(years_x)
        axe.tick_params(axis='x', rotation=90, labelsize=10)
        axe.tick_params(axis='y', labelsize=10)
        axe.bar(years1, skills1, label='для всех вакансий ', width=0.4)
        axe.bar(years2, skills2, label='для ' + str(self.vac_name), width=0.4)
        axe.grid(axis='y')
        axe.legend(fontsize=10)
        for i in range(8):
            plt.text(2015 + i - 0.3, 5, labels1[i], rotation=90, fontsize=12, color='w')
        for i in range(8):
            plt.text(2015 + i + 0.05, skills2[i] + 5, labels2[i], rotation=90, fontsize=12, color='k')
        plt.savefig('report/skills_by_years.png')

    def generate_pdf(self, image_names):
        """Генерирует pdf-файл со статистикой
        Args:
            image_names ([str]): имя png-файла с графиками
        """
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template("template.html")

        pdf_template = template.render({'vac_name': self.vac_name,
                                        'image_files': image_names,
                                        'years': list(YEARS_NULL_DICT.keys()),
                                        'salary_by_year': self.salary_by_year,
                                        'count_salary_by_year': self.count_salary_by_year,
                                        'salary_by_year_by_vacancy': self.salary_by_year_by_vacancy,
                                        'count_salary_by_year_by_vacancy': self.count_salary_by_year_by_vacancy,
                                        'cities_salaries': list(self.salary_by_city.keys()),
                                        'salary_by_city': self.salary_by_city,
                                        'cities_part': list(self.part_salary_by_city.keys()),
                                        'part_salary_by_city': self.procent_salary_by_city,
                                        'skills': [list(self.skills_by_year[year].keys())[0] for year in
                                                   range(2015, 2023)],
                                        'skills_values': [list(self.skills_by_year[year].values())[0] for year in
                                                          range(2015, 2023)],
                                        'skills_param': [list(self.skills_by_year_param[year].keys())[0] for year in
                                                         range(2015, 2023)],
                                        'skills_values_param': [list(self.skills_by_year_param[year].values())[0] for
                                                                year in range(2015, 2023)],
                                        'best_skill': self.data_set.best_skill,
                                        'best_skill_score': self.data_set.best_skill_score,
                                        'best_skill_param': self.data_set.best_skill_param,
                                        'best_skill_score_param': self.data_set.best_skill_score_param,
                                        })

        config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
        options = {'enable-local-file-access': None}
        pdfkit.from_string(pdf_template, 'report/report.pdf', configuration=config, options=options)
