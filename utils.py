from consts import CURRENCY_TO_RUB


def clean_int_point(number):
    """Убирает символы '.0' в конце входной строки, используется для корректоного отображения чисел
    Args:
     number (str): число в виде строки
    Returns:
         str: число в виде строки без '.0'
    """
    if '.0' in number:
        number = number[:-2]
    return number


def convert_data(string):
    """ Преобразует дату в читаемый вид для корректного отображения

    Args:
     string (str): дата вида '2022-07-05T18:19:30+0300'
    Returns:
        str: дата вида '05.07.2022'
    """
    day = string[8:10]
    month = string[5:7]
    year = string[:4]
    return day + '.' + month + '.' + year


def calculate_salary_rating(vacancies):
    """ Считает среднюю зарплату из списка вакансий с учётом разных валют

    Args:
     vacancies: список вакансий типа Vacancy
    Returns:
         int: средняя зарплата
    """
    if len(vacancies) == 0:
        return 0
    medium_salary = 0
    for vacancy in vacancies:
        coef = CURRENCY_TO_RUB[vacancy.salary_currency]
        medium_salary += (int(clean_int_point(vacancy.salary_from)) + int(
            clean_int_point(vacancy.salary_to))) * coef // 2
    return medium_salary // len(vacancies)
