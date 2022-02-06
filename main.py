import sys
import sqlite3

import pygame
from random import choice
from PyQt5 import QtGui, uic, QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidgetItem
from PyQt5.QtWidgets import QTextEdit, QMainWindow, QMessageBox

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling,
                                        True)  # это чтобы программу не контузило, если у вас широкоформатный монитор

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)  #


class FirstForm(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('mainwin.ui', self)
        self.connection = sqlite3.connect("recipes.sqlite")
        self.zapros.setPlainText("Все")  # Первоначальный вывод базы данных без необходимости нажимать кнопку
        self.zapusk()

        self.cmd.setReadOnly(True)
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.button_db_to_txt.clicked.connect(self.db_to_txt_file)
        self.button_db_to_csv.clicked.connect(self.db_to_csv_file)
        self.button_zapusk.clicked.connect(self.zapusk)
        self.button_save.clicked.connect(self.save)  # соединение всех кнопок и функций
        self.button_OK.clicked.connect(self.add)
        self.button_delete.clicked.connect(self.delete)
        self.button_music.clicked.connect(self.music_ON_OFF)
        self.compendium.clicked.connect(self.comped)

        sp = ['Haggstrom.mp3', 'Minecraft.mp3', 'Key.mp3', 'Subwoofer lullaby.mp3']
        self.flag = False
        pygame.mixer.init()
        self.song2 = pygame.mixer.Sound(choice(sp))  # включение случайной музыки из списка :)
        self.song2.play(-1)
        self.song2.set_volume(0)

    def comped(self):  # функция открытия второго класса для вывода справочника
        pygame.mixer.music.play(0)
        self.shw = SecondForm(self)
        self.shw.show()

    def music_ON_OFF(self):  # функция включения/выключения музыки
        pygame.mixer.music.play(0)
        if self.flag:
            self.song2.set_volume(0)
            self.flag = False
        elif self.flag is False:
            self.song2.set_volume(0.2)
            self.flag = True

    def zapusk(self):  # функция выполнения запроса из поля для ввода
        self.button_save.setText('Сохранить')
        self.button_zapusk.setText('Запуск')
        pygame.mixer.init()
        pygame.mixer.music.load('baton.mp3')
        pygame.mixer.music.play(0)
        pygame.mixer.music.set_volume(0.2)
        self.query = self.zapros.toPlainText()
        self.query = self.query.lower()
        if self.query == 'все' or self.query == 'всё':
            self.query = 'SELECT * FROM dishes'
        elif 'где' in self.query:
            self.splitt = self.query.split()
            self.slot = self.splitt[1]
            self.znak = self.splitt[2]
            self.number = self.splitt[
                3]  # number не всегда является числом. Если мы хотим найти рецепт по названию, тогда это уже никакой не number
            if (self.slot == 'название' or self.slot == 'рецепт' or self.slot == 'ингредиенты') and (
                    self.znak == '<' or self.znak == '>'):  # мы не можем сравнивать название, рецепт и ингредиенты, поэтому уведомляем об этом пользователя
                print('Неподходящий знак для этого слота')
            if self.number.isdigit() is False:
                self.query = f'SELECT * FROM dishes WHERE {self.slot} LIKE "{self.number}"'  # если number все-таки не число, тогда мы ищем все совпадения в базе данных
            else:
                self.query = f'SELECT * FROM dishes WHERE {self.slot} {self.znak} {self.number}'  # но если number окажется число, то тогда мы уже будем что-то сравнивать

        self.flag = True  # если ошибки в запросе нет - выводим таблицу. Если ошибка есть - вместо вылета программы выводим сообщение в консоль
        try:
            self.result = self.connection.cursor().execute(self.query).fetchall()
            if self.flag:
                self.table.setColumnCount(6)
                self.table.setRowCount(0)
                self.table.setHorizontalHeaderLabels(['номер', 'название', 'время', 'рецепт', 'ингредиенты', 'калории'])
                for i, row in enumerate(self.result):
                    self.table.setRowCount(  # все это - обычный вывод всей базы данных в удобное окно для просмотра
                        self.table.rowCount() + 1)
                    for j, elem in enumerate(row):
                        self.table.setItem(i, j, QTableWidgetItem(str(elem)))
            print('Запущено')
        except Exception:
            print(
                'Некорректно введенный запрос. Повторите попытку.')  # ой-ой. Уведомляем пользователя о том, что он где-то ошибся.
            self.button_zapusk.setText('Ошибка!')
            self.flag = False

    def db_to_txt_file(self):  # функция конвертирования базы данных в .txt
        pygame.mixer.music.play(0)
        f = open('database.txt', 'w')
        f.write('Номер;название;время;рецепт;ингредиенты;калории')
        self.result = self.connection.cursor().execute('SELECT * FROM dishes').fetchall()
        for elem in self.result:
            f.write('\n')
            txt = str(elem[0]) + ';' + str(elem[1]) + ';' + str(elem[2]) + ';' + str(elem[3]) + ';' + str(
                elem[4]) + ';' + str(elem[5])
            f.write(txt)
        f.close()

    def db_to_csv_file(self):  # функция конвертирования базы данных в .csv
        pygame.mixer.music.play(0)
        with open('database.csv', 'w') as csvfile:
            csvfile.write('Номер;название;время;рецепт;ингредиенты;калории')
            self.result = self.connection.cursor().execute('SELECT * FROM dishes').fetchall()
            for elem in self.result:
                csvfile.write('\n')
                txt = str(elem[0]) + ';' + str(elem[1]) + ';' + str(elem[2]) + ';' + str(elem[3]) + ';' + str(
                    elem[4]) + ';' + str(elem[5])
                csvfile.write(txt)
        csvfile.close()

    def add(self):  # функция добавления нового элемента в базу данных
        self.button_save.setText('Сохранить')
        pygame.mixer.music.play(0)
        self.cmd.setText('')
        if self.vvod1.text() == '' or self.vvod2.text() == '' or self.vvod3.text() == '' or self.vvod4.text() == '' or self.vvod5.text() == '':
            self.cmd.setText('Заполните все окна ввода')
        elif self.vvod2.text().isdigit() is False or self.vvod5.text().isdigit() is False:
            self.cmd.setText(
                'Тип данных не подходит. Введите цифры.')  # собираем данные, и, в случае, если пользователь ввел что-то не то, говорим ему об этом
        elif self.vvod0.text() != '':  # если пользователь ввел номер - тогда просто добавляем элемент в базу данных
            if self.vvod0.text().isdigit() is False:
                self.cmd.setText('Тип данных не подходит. Введите цифры.')
            else:
                num = self.vvod0.text()
                name = self.vvod1.text()
                time = self.vvod2.text()
                time = int(time)
                recipe = self.vvod3.text()
                ingredients = self.vvod4.text()
                calories = self.vvod5.text()
                calories = int(calories)
                res = self.connection.cursor().execute(
                    f"INSERT INTO dishes('номер', 'название', 'время', 'рецепт', 'ингредиенты', 'калории') VALUES({num}, '{name}', {time}, '{recipe}', '{ingredients}', {calories})").fetchall()
                self.cmd.setText('Добавление элемента в базу данных завершено успешно!')
        else:  # если же номер пустой - то ищем максимальное значение номера в бд и прибавляем значение 1
            archive = self.connection.cursor().execute(self.query).fetchall()
            sp = []
            for elem in archive:
                sp.append(elem[0])
            num = int(max(sp)) + 1
            name = self.vvod1.text()
            time = self.vvod2.text()
            time = int(time)
            recipe = self.vvod3.text()
            ingredients = self.vvod4.text()
            calories = self.vvod5.text()
            calories = int(calories)
            res = self.connection.cursor().execute(
                f"INSERT INTO dishes('номер', 'название', 'время', 'рецепт', 'ингредиенты', 'калории') VALUES({num}, '{name}', {time}, '{recipe}', '{ingredients}', {calories})").fetchall()
            self.cmd.setText('Добавление элемента в базу данных завершено успешно!')

    def delete(self):  # функция удаления выделенных элементов в бд
        self.button_save.setText('Сохранить')
        pygame.mixer.music.play(0)
        rows = list(set([i.row() for i in self.table.selectedItems()]))
        ids = [self.table.item(i, 0).text() for i in rows]
        valid = QMessageBox.question(
            self, 'Удаление', "Действительно удалить элементы с id " + ",".join(ids),
            # вызов всплывающего окна с подтверждением удаления
            QMessageBox.Yes, QMessageBox.No)
        if valid == QMessageBox.Yes:  # если пользователь подтвердил - удаляем.
            cur = self.connection.cursor()
            cur.execute("DELETE FROM dishes WHERE номер IN (" + ", ".join(
                '?' * len(ids)) + ")", ids)

    def save(self):  # функция просто сохраняет все изменения
        self.button_save.setText('Сохранено!')
        pygame.mixer.music.play(0)
        self.connection.commit()

    def closeEvent(self, event):
        self.connection.close()
        self.song2.stop()

    def except_hook(cls, exception,
                    traceback):  # функция выводит ошибку в консоль, вместо того, чтобы вылететь без ошибки
        sys.__excepthook__(cls, exception, traceback)


class SecondForm(QWidget):  # второй класс, который открывает окно с краткой информацией
    def __init__(self, *args):
        super().__init__()
        self.initUI(args)

    def initUI(self, args):
        self.setGeometry(300, 300, 400, 300)
        self.setWindowTitle('Справочник')
        self.setStyleSheet('background-color: (235, 222, 207)')

        self.label = QTextEdit('Регистр не важен. Введите !ОДНУ! из перечисленных команд в основном поле для ввода команд в разделе Main, после этого нажмите на кнопку запустить или удалить. \
                               Все (Всё) - самодостаточная команда, выводит всю базу данных. Где - после команды необходимо указать необходимый слот для сортировки (например, время или калории(маленькими буквами)) \
                               и один из символов - больше, меньше или равно. Не забывайте ставить пробелы после каждого слова, иначе ничего не заработает. \
                               Несомненно, вы можете использовать обычные запросы SQLite, например, SELECT *, DELETE, INSERT.',
                               self)
        self.label.resize(400, 300)
        self.label.setReadOnly(True)  # запрещаем вносить изменения в текст


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FirstForm()
    ex.show()
    sys.excepthook = FirstForm.except_hook
    sys.exit(app.exec())
