import requests
from datetime import datetime
import os
from abc import ABC, abstractmethod
import json


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


class HH(Vakancy, FuncForApi):
    def __init__(self, name, page, count):
        super().__init__(name, page, count)
        self.url = 'https://api.hh.ru/vacancies'


    def get_vacancies(self):
        """ Данные будут сохраняться в словарь"""

        data = requests.get(f'{self.url}', params={'text': self.name, 'page': self.page, 'per_page': self.count}).json()
        return data

    def load_vacancy(self):
        """ данные  ->'vacancies' """
        data = self.get_vacancies()
        vacancies = []
        for vacancy in data.get('items', []):
            published_at = datetime.strptime(vacancy['published_at'], "%Y-%m-%dT%H:%M:%S%z")
            vacancy_info = {
                'id': vacancy['id'],
                'name': vacancy['name'],
                'solary_ot': vacancy['salary']['from'] if vacancy.get('salary') else None,
                'solary_do': vacancy['salary']['to'] if vacancy.get('salary') else None,
                'responsibility': vacancy['snippet']['responsibility'],
                'data': published_at.strftime("%d.%m.%Y")
            }
            vacancies.append(vacancy_info)

        return vacancies

def job(number_of_platform):
    """ Основная функция: принимает данные от пользователя. Согласно им сортируются и вносятся в файл job.json """
    name = input('Введите вакансию: ')
    count = int(input('Введите кол-во вакансий: '))
    page = int(input('Введите страницу: '))
    sj = SJ(name, page, count)
    hh = HH(name, page, count)
    dict_for_job = {'SJ': sj.load_vacancy(), 'HH': hh.load_vacancy()}

    with open('job.json', 'w', encoding='utf-8') as file:
        json.dump(dict_for_job, file, ensure_ascii=False, indent=2)
        if number_of_platform == '1':
            while True:
                hh.page = page
                data_for_hh = hh.load_vacancy()
                dict_for_job['HH'] = data_for_hh
                with open('job.json', 'w', encoding='utf-8') as file:
                    json.dump(dict_for_job, file, ensure_ascii=False, indent=2)
                for platform in dict_for_job['HH']:
                    if platform['solary_to'] == 'null':
                        print(f"\nid: {platform['id']}\nДолжность:"f"{platform['name']}\n"
                              f"З/п: договорная\n"
                              f"Описание:{platform['responsibility']}\n"
                              f"Дата:{platform['data']}\n")
                        break
                    if platform['solary_do'] == 'null':
                        print(f"\nid: {platform['id']}\nДолжность:"f"{platform['name']}\n"
                              f"З/п:{platform['solary_ot']}\n"
                              f"Описание:{platform['responsibility']}\n"
                              f"Дата:{platform['data']}\n")
                    else:
                        print(f"\nid: {platform['id']}\nДолжность:"f"{platform['name']}\n"
                              f"З/п: {platform['solary_ot']} - {platform['solary_do']}\n"
                              f"Описание:{platform['responsibility']}\n"
                              f"Дата:{platform['data']}\n")
                vvod = input('перейти на следующую страницу? y/n ')
                if vvod == 'y':
                    page += 1
                else:
                    break

        if number_of_platform == '2':
            while True:
                sj.page = page
                data_for_sj = sj.load_vacancy()
                dict_for_job['SJ'] = data_for_sj

                with open('job.json', 'w', encoding='utf-8') as file:
                    json.dump(dict_for_job, file, ensure_ascii=False, indent=2)

                for platform in dict_for_job['SJ']:
                    if platform['solary_to'] == 'null':
                        print(f"\nid: {platform['id']}\nДолжность:"f"{platform['name']}\n"
                              f"З/п: договорная\n"
                              f"Описание:{platform['responsibility']}\n"
                              f"Дата:{platform['data']}\n")
                        break
                    if platform['solary_do'] == 'null':
                        print(f"\nid: {platform['id']}\nДолжность:"f"{platform['name']}\n"
                              f"З/п:{platform['solary_ot']}\n"
                              f"Описание:{platform['responsibility']}\n"
                              f"Дата:{platform['data']}\n")
                    else:
                        print(f"\nid: {platform['id']}\nДолжность:"f"{platform['name']}\n"
                              f"З/п: {platform['solary_ot']} - {platform['solary_do']}\n"
                              f"Описание:{platform['responsibility']}\n"
                              f"Дата:{platform['data']}\n")
                vvod = input('перейти на следующую страницу? y/n ')
                if vvod == 'y':
                    page += 1
                else:
                    break
        else:
            while True:
                hh.page = page
                sj.page = page
                data_for_hh = hh.load_vacancy()
                data_for_sj = sj.load_vacancy()

                dict_for_job['HH'] = data_for_hh
                dict_for_job['SJ'] = data_for_sj

                with open('job.json', 'w', encoding='utf-8') as file:
                    json.dump(dict_for_job, file, ensure_ascii=False, indent=2)

                for platform, data in dict_for_job.items():
                    print(f"\nПлатформа: {platform}")
                    for item in data:
                        if item['solary_ot'] == 'null':
                            print(f"\nid: {platform['id']}\nДолжность: "f"{platform['name']}\n"
                                  f"З/п: договорная\n"
                                  f"Описание:{platform['responsibility']}\n"
                                  f"Дата:{platform['data']}\n")
                            continue
                        if item['solary_do'] == 'null':
                            print(
                            f"id:{item['id']}\n"
                            f"Должность:{item['name']}\n"
                            f"З.п:{item['solary_ot']}\n"
                            f"Описание:{item['responsibility']}\n"
                            f"Дата:{item['data']}\n")
                        else:
                            print(
                                f"id:{item['id']}\n"
                                f"Должность:{item['name']}\n"
                                f"З.п: {item['solary_ot']} - {item['solary_do']} \n" 
                                f"Описание:{item['responsibility']}\n"
                                f"Дата:{item['data']}\n")

                vvod = input('перейти на следующую страницу? y/n ')
                if vvod == 'y':
                    page += 1
                else:
                    break




