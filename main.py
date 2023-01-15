from consts import YEARS_NULL_DICT, RUS_HEAD, RUS_HEAD_FOR_PRINT
from utils import clean_int_point, convert_data, calculate_salary_rating
from DataSet import DataSet
from Report import Report

file_name = 'vacancies_with_skills.csv'  # input('Введите название файла: ')
vac_name = 'Python - разработчик'  # input('Введите название профессии: ')

data_set = DataSet(file_name, vac_name)
new_report = Report(data_set, vac_name)

print(new_report.salary_by_year)
print(new_report.salary_by_year_by_vacancy)
print(new_report.count_salary_by_year)
print(new_report.count_salary_by_year_by_vacancy)
print(new_report.salary_by_city)
print(new_report.part_salary_by_city)
print(new_report.skills_by_year)
print(new_report.skills_by_year_param)


new_report.generate_excel()
new_report.generate_image()
new_report.generate_pdf(["salary_rating_by_years.png", "salary_count_by_years.png", "salary_rating_by_cities.png",
                         "part_count_by_sities.png", "skills_by_years.png"])
