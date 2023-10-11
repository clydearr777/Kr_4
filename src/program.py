import requests
from datetime import datetime
import json
import os
from abc import ABC, abstractmethod


class FuncForApi(ABC):
    """ абстрактный класс и абстрактный метод get_vacanties: будет принимать вакансии и возвращать список"""

    @abstractmethod
    def get_vacancies(self):
        pass


class Vakancy:
    """ класс, на основе которого будет строиться дочерний класс SJ """
    def __init__(self, name, page, count):
        self.name = name
        self.page = page
        self.count = count

    def __repr__(self):
        return f'{self.name}'


class SJ(Vakancy, FuncForApi):
    def __init__(self, name, page, count):
        super().__init__(name, page, count)
        self.url = 'https://api.superjob.ru/2.0/vacancies/'

    def get_vacancies(self):
        """Выгрузка данных по 'Super_job' по запросам пользователя  по АПИ - ключу и возвращается словарь
            название ключа SJ_PI_KEY """

        headers = {
                    'X-Api-App-Id': os.getenv('SJ_API_KEY'),
                }
        data = requests.get(self.url, headers=headers, params={'keywords': self.name, 'page': self.page, 'count': self.count}).json()
        return data

    def load_vacancy(self):
        """Запускаем цикл, собираем нужные нам данные, помещаем все в 'vacancy_list' """
        data = self.get_vacancies()
        vacancy_list = []
        for vacant in data['objects']:
            published_at = datetime.fromtimestamp(vacant.get('date_published', ''))
            super_job = {
                'id': vacant['id'],
                'name': vacant.get('profession', ''),
                'solary_ot': vacant.get('payment_from', '') if vacant.get('payment_from') else None,
                'solary_do': vacant.get('payment_to') if vacant.get('payment_to') else None,
                'responsibility': vacant.get('candidat').replace('\n', '').replace('•', '') if vacant.get('candidat') else None,
                'data': published_at.strftime("%d.%m.%Y"),

            }
            vacancy_list.append(super_job)
        return vacancy_list


def job():
    """ Основная функция проекта: принимает данные от пользователя, согласно им сортируются и вносятся в файл job.json """
    name = input('Введите вакансию: ')
    count = input('Введите кол-во вакансий: ')
    page = int(input('Введите страницу: '))
    sj = SJ(name, page, count)
    dict_for_job = {'SJ': sj.load_vacancy()}

    with open('Super_job.json', 'w', encoding='utf-8') as file:
        json.dump(dict_for_job, file, ensure_ascii=False, indent=2)

    while True:
        sj.page = page
        sj_data = sj.load_vacancy()
        dict_for_job['SJ'] = sj_data

        with open('job.json', 'w', encoding='utf-8') as file:
            json.dump(dict_for_job, file, ensure_ascii=False, indent=2)

        for platform in dict_for_job['SJ']:
            print(f"\nid - {platform['id']}\nДолжность: {platform['name']}\nЗарплата: {platform['solary_ot']} - {platform['solary_do']}\nОписание: {platform['responsibility']}\nДата: {platform['data']}\n")

        a = input('Показать следующую страницу? y/n ')
        if a == 'y':
            page += 1
        else:
            break

job()

