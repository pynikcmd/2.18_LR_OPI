#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import datetime
import json
import os.path
import sys
from dotenv import load_dotenv


def add_person(staff, name, number, birthday):
    """
    Запросить данные о человеке.
    """
    bday = list(map(int, birthday.split(".")))
    date_bday = datetime.date(bday[2], bday[1], bday[0])
    staff.append(
        {
            "name": name,
            "phone": number,
            "birthday": date_bday
        }
    )

    return staff


def display_people(staff):
    """
    Отобразить список работников.
    """
    # Проверить, что список работников не пуст.
    if staff:
        # Заголовок таблицы.
        line = "+-{}-+-{}-+-{}-+-{}-+".format(
            "-" * 4,
            "-" * 30,
            "-" * 15,
            "-" * 15
        )
        print(line)
        print(
            "| {:^4} | {:^30} | {:^15} | {:^15} |".format(
                "№",
                "Фамилия и имя",
                "Телефон",
                "День рождения"
            )
        )
        print(line)

        # Вывести данные о всех сотрудниках.
        for idx, human in enumerate(staff, 1):
            print(
                f"| {idx:>4} |"
                f' {human.get("name", ""):<30} |'
                f' {human.get("phone", 0):<15} |'
                f' {human.get("birthday")}      |'
            )
            print(line)

    else:
        print("Список пуст.")


def find_nomer(staff, nomer):
    """
    Выбрать работников с заданным стажем.
    """
    # Сформировать список людей.
    result = []
    for n in staff:
        if nomer in str(n.values()):
            result.append(n)

    # Проверка на наличие записей
    if len(result) == 0:
        return print("Запись не найдена")

    # Возвратить список выбранных работников.
    return result


def json_deserial(obj):
    """
    Деериализация объектов datetime
    """
    for i in obj:
        if isinstance(i["birthday"], str):
            i["birthday"] = datetime.datetime.strptime(i["birthday"], '%Y-%m-%d').date()


def load_people(file_name):
    """
    Загрузить всех работников из файла JSON.
    """
    # Открыть файл с заданным именем для чтения.
    with open(file_name, "r", encoding="utf-8") as fin:
        return json.load(fin)


def json_serial(obj):
    """Сериализация объектов datetime"""

    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()


def save_people(file_name, staff):
    """
    Сохранить всех работников в файл JSON.
    """
    # Открыть файл с заданным именем для записи.
    with open(file_name, "w", encoding="utf-8") as fout:
        # Выполнить сериализацию данных в формат JSON.
        # Для поддержки кирилицы установим ensure_ascii=False
        json.dump(staff, fout, ensure_ascii=False, indent=4, default=json_serial)


def main(command_line=None):
    """
    Главная функция программы.
    """
    # Создать родительский парсер для определения имени файла.
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        "-d",
        "--data",
        action="store",
        required=False,
        help="The data file name"
    )

    # Создать основной парсер командной строки.
    parser = argparse.ArgumentParser("people")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )

    subparsers = parser.add_subparsers(dest="command")

    # Создать субпарсер для добавления работника.
    add = subparsers.add_parser(
        "add",
        parents=[file_parser],
        help="Добавить нового человека"
    )

    add.add_argument(
        "-n",
        "--name",
        action="store",
        required=True,
        help="Это имя человека"
    )

    add.add_argument(
        "-nm",
        "--number",
        type=int,
        action="store",
        help="Номер телефона человека"
    )

    add.add_argument(
        "-bd",
        "--bday",
        action="store",
        required=True,
        help="Дата рождения"
    )

    # Создать субпарсер для отображения всех людей.
    _ = subparsers.add_parser(
        "display",
        parents=[file_parser],
        help="Отобразить всех людей"
    )

    # Создать субпарсер для поиска людей по фамилии.
    find = subparsers.add_parser(
        "find",
        parents=[file_parser],
        help="Найти человека"
    )

    find.add_argument(
        "-nom",
        "--nomer",
        action="store",
        required=True,
        help="Обязательный номер"
    )

    # Выполнить разбор аргументов командной строки.
    args = parser.parse_args(command_line)
    # Получить имя файла.
    data_file = args.data

    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    if not data_file:
        data_file = os.environ.get("PEOPLE_DATA")
    if not data_file:
        print("The data file name is absent", file=sys.stderr)
        sys.exit(1)

    # Загрузить всех работников из файла, если файл существует.
    is_dirty = False
    if os.path.exists(data_file):
        people = load_people(data_file)
    else:
        people = []

    # Добавить челоека.
    if args.command == "add":
        people = add_person(
            people,
            args.name,
            args.number,
            args.bday
        )
        is_dirty = True

    # Отобразить всех людей.
    elif args.command == "display":
        display_people(people)

    # Выбрать требуемых рааботников.
    elif args.command == "find":
        selected = find_nomer(people, args.nomer)
        display_people(selected)

    # Сохранить данные в файл, если список работников был изменен.
    if is_dirty:
        save_people(args.filename, people)


if __name__ == "__main__":
    main()
