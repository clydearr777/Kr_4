from src.program import job

"""
в файле ничего лишнего: отвечает только за работу с пользователем
"""


number_of_platform = input(str('Выберите на каком ресурсе произвести поиск: (1 - HH.ru, 2 - super.ru, 3 - оба ресурса)  '))

job(number_of_platform)