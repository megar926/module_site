# -*- coding: utf-8 -*-
#
import pandas as pd
import numpy as np
import re
import datetime
#from fuzzywuzzy import fuzz
import os

class Convertbomfile():

    def loadBase(self, path_eri, path_conn):
        try:
            print('Загрузка базы данных.........................................')
            self.base_intermech = pd.read_excel(path_eri)
            print('OK: Файл базы данных загружен\n')
        except FileNotFoundError:
            print('ERROR: Файл базы данных не загружен\n')

        try:
            print(path_conn)
            self.base_intermech_conn = pd.read_excel(path_conn)
            print(self.base_intermech_conn.columns)
            self.base_intermech = self.base_intermech.append(self.base_intermech_conn, ignore_index=True)
            print('OK: Файл базы данных соединителей загружен\n')

        except FileNotFoundError:
            print('ERROR: Файл базы данных соединителей не загружен\n')

        return self.base_intermech


    def create_func(self, list0, list1, list2):
        obr_list = []
        for x, y, z in zip(list0, list1, list2):
            if ((str(x)) != 'nan'):
                obr_list.append(str(x).lstrip() + '_' + str(y))
            else:
                obr_list.append(str(z).lstrip() + '_' + str(y))
        return obr_list

    def makeup(self, name):
        return str(name).upper().rstrip().lstrip()


    def cadence_name(self, name):
        name = name.upper()
        name = name.replace('\xa0', '')
        no_sym_list = ['-', '+', '–', '%', ' ', '±', '«', '»', '.', '"', '/', '\\', '*', '#', '‑']
        alf_dict = {'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'JO',
                    'Ж': 'ZH', 'З': 'ZH', 'И': 'I', 'Й': 'JJ', 'К': 'K', 'Л': 'L', 'У': 'U', 'Р': 'R', 'О': 'O', 'М': 'M',
                    'И': 'I', 'Н': 'N', 'Т': 'T',
                    'Ф': 'F', "Х": "KH", 'Ц': 'C', 'Ч': 'CH', 'Ш': 'SH', 'Щ': 'SHH', 'Ы': 'Y', 'Э': 'EH',
                    'Ю': 'JU', 'Я': 'JA', 'П': 'P', 'С': 'S'}
        class_elem = ['МИКРОСХЕМА', 'РЕЗИСТОР', 'КОНДЕНСАТОР', 'ТРАНЗИСТОР', 'ДИОД', 'РЕЗИСТОРНАЯ СБОРКА', 'ТРАНСФОРМАТОР',
                      'ДРОССЕЛЬ',
                      'БЛОК ТРАНСФОРМАТОРОВ', 'СБОРКА ТРАНЗИСТОРНАЯ', 'ТРАНЗИСТОРНАЯ СБОРКА', 'СТАБИЛИТРОН',
                      'ПРЕДОХРАНИТЕЛЬ', 'ТЕРМОДАТЧИК', 'КЛЕММА',
                      'РЕЛЕ', 'ФИЛЬТР ПОМЕХОПОДАВЛЯЮЩИЙ', 'ТЕРМОРЕЗИСТОР', 'БЛОК РЕЗИСТОРОВ']

        tu = re.search(r'\w+[.]\d+[.]\d+[' ']*ТУ[\w,\s,-]*', name)
        if (tu):
            tu = re.search(r'\w+[.]\d+[.]\d+[' ']*ТУ[\w,\s,-]*', name).group()
        else:
            tu = ''

        name_ic = name.replace(tu, '')
        for x in class_elem:
            if (x in name_ic):
                name_ic = name_ic.replace(x, '')

        # Обработка ТУ
        tu = tu.replace('ТУ', '')
        tu = tu.replace(' ', '')
        tu = tu.replace('.', '')
        tu = tu[-6:]

        # Обработка названия микросхемы
        name_ic_copy = name_ic
        for x in list(name_ic_copy):
            if (x in no_sym_list):
                name_ic = name_ic.replace(x, '')

        name_ic_copy = name_ic
        for x in list(name_ic_copy):
            if (x in alf_dict.keys()):
                name_ic = name_ic.replace(x, alf_dict[x])

        # Находим числа с разделителями запятая
        ch = re.findall(r'\d+[,]\d+', name_ic)

        if (ch):
            for x in ch:
                name_ic = name_ic.replace(',', '-')
        else:
            ch = ''
        cadence = (name_ic + tu)
        return cadence


    def convert_cn(self, path):
        if ((True)):
            self.name_file = path
            file_type = path.split('.')[-1]
            if file_type == 'html':
                self.bomData = pd.read_html(self.name_file)[1]
                self.bomData.columns = self.bomData.iloc[0]
                self.bomData = self.bomData.drop(0)
                self.bomData = self.bomData.drop(len(self.bomData['Qty'].tolist()))
            elif file_type == 'xlsx':
                self.bomData = pd.read_excel(self.name_file)
            else:
                print('Выбраный файл иммеет не верный формат!\n')
            self.bomData['PART_NUMBER'] = self.bomData['PART_NUMBER'].replace('NC', 'ЭЛЕМЕНТ ПЕЧАТНОГО МОНТАЖА')
            self.bomData['PART_NUMBER'] = self.bomData['PART_NUMBER'].replace('?', 'ЭЛЕМЕНТ ПЕЧАТНОГО МОНТАЖА')
            self.bomData['Qty'] = self.bomData['Qty'].astype(int)
            note_rus = []

            self.bomData['NOTE'].replace('-', '', inplace=True)
            self.bomData['NOTE'].replace(np.nan, '', inplace=True)
            self.bomData['NOTE'].replace('?', '', inplace=True)  #
            note_star = self.bomData['NOTE'].tolist()
            note_star_ = []
            for x in note_star:
                note_star_.append(x.replace('*', '✽'))
            self.bomData['NOTE'] = note_star_
            for num, x in enumerate(self.bomData['NOTE'].tolist()):
                starsQty = str(x).count('✽')
                if (starsQty > 0):
                    note_rus.append(f", Примечание {starsQty}")
                else:
                    note_rus.append("")
            self.bomData['NOTE_RUS'] = note_rus
            self.bomData['JEDEC_TYPE'] = self.bomData['JEDEC_TYPE'] + self.bomData['NOTE_RUS']
            self.bomData['Ref Des'] = self.bomData['Ref Des'] + self.bomData['NOTE']
            self.bomData = self.bomData[['Ref Des', 'PART_NUMBER', 'Qty', 'JEDEC_TYPE']]
            self.bomData['PART_NUMBER'] = self.bomData['PART_NUMBER'].astype(str)
            self.bomData = self.bomData[self.bomData['Qty']>0]
            print(self.bomData['JEDEC_TYPE'])
            print('\n')
            stat, pathBomFile = self.convert_bom(self.bomData)
            return stat, pathBomFile
        else:
            print('--------Вы не выбрали файл---------\n')

    def stripl(self, x):
        try:
            x = str(x).lstrip().rstrip()
            return x
        except:
            return x

    def convert_bom(self, out):
        start = datetime.datetime.now()
        if ((True)):
            note = []
            bom = out
            data = self.base_intermech
            line_0 = ''
            line_1 = ''
            line_2 = ''
            line_3 = ''
            line_4 = ''
            if (len(line_0) > 0):
                note.append(line_0)
            if (len(line_1) > 0):
                note.append(line_1)
            if (len(line_2) > 0):
                note.append(line_2)
            if (len(line_3) > 0):
                note.append(line_3)
            if (len(line_4) > 0):
                note.append(line_4)

            Cadence_Name = 'PART_NUMBER'
            Ref = 'Ref Des'
            Count = 'Qty'
            Path = 'JEDEC_TYPE'
            must_index = [Cadence_Name, Ref, Count, Path]

            for x in must_index:
                if x not in bom.columns.to_list():
                    print('Не верное название колонок в BOM файле')
            try:
                bom['Вариант'] = pd.Series([0 for x in range(len(bom[Cadence_Name]))])
                var_idx = []
                new_list = []
                new_list_class = []
                new_list_firm = []
                new_list_func = []
                new_list_assembly_note = []
                not_in_base_list = []
                bom[Cadence_Name] = bom[Cadence_Name].apply(lambda x: self.stripl(x))
                bomCadenceName = bom[Cadence_Name].to_list()
                data['Cadence_Name'] = data['Cadence_Name'].apply(lambda x: self.stripl(x))
                dataCadenceName = data['Cadence_Name'].to_list()
                for x in bomCadenceName:
                    if (x not in dataCadenceName):
                        not_in_base_list.append(str(x))
                    else:
                        rowData = data[data['Cadence_Name'] == x]
                        new_list.append(str(rowData['Наименование']))
                        new_list_class.append(str(rowData['Класс']))
                        new_list_firm.append(str(rowData['Фирма изготовитель']))
                        new_list_func.append(str(rowData['Функциональное назначение']))
                        new_list_assembly_note.append(str(rowData['Примечание для производства']))
                        # if int(data[data['Cadence_Name'] == x]['Вариант'])>=0:
                        #    var_idx.append(int(data[data['Cadence_Name'] == x]['Вариант']))
                        # else:
                        #    var_idx.append(int(0))
                        var_idx.append(int(0))
                print(datetime.datetime.now() - start)
                # for x in not_in_base_list:
                #     for y in dataCadenceName:
                #         try:
                #             ratio = fuzz.ratio(x, y)
                #             if ratio>95:
                #                 print(x, y, ratio, len(x), len(y))
                #                 for num, x1 in enumerate(list(x)):
                #                     if(x1 != list(y)[num]):
                #                         print(num, x1)
                #                 for num, x1 in enumerate(list(y)):
                #                     if(x1 != list(x)[num]):
                #                         print(num, x1)
                #         except:
                #             pass
                if len(not_in_base_list) > 0:
                    print(
                        f'Элементы {pd.Series(not_in_base_list).unique()} отсутствуют в базе интермеха, необходимо добавить элемент в базу!\n\n')
                    return(False, pd.Series(not_in_base_list).unique())
                # Обработка примечаний
                bom['Примечание ПЭ'] = bom[Path]
                bom = bom.replace(np.nan, '-')
                bom['Примечания'] = bom['Примечание ПЭ'].str.split(',')
                primech = []
                for num0, x in enumerate(bom['Примечание ПЭ'].tolist()):
                    if (re.findall(r'[П-п]{1}римеч', x)):
                        if (re.findall(', ', x)):
                            for num, y in enumerate(x.split(',')):
                                if re.findall(r'[П-п]{1}римеч', y):
                                    y = y.lstrip()
                                    y = y.rstrip()
                                    y = y.title()
                                    primech.append(y)
                                else:
                                    continue
                        else:
                            primech.append('-')
                    else:
                        primech.append('-')
                bom['Примечания'] = primech
                bom = bom.replace('-', np.nan)
                print(f'\nКоличество созданных элементов: {len(new_list)}\n')
                print(f'Количество элементов по столбцу "Кол-во": {len(bom[Cadence_Name].tolist())}\n')
                print(f'Количество уникальных элементов: {len(pd.Series(bom[Cadence_Name].unique()))}\n')
                bom['Наименование'] = new_list
                # Обработка типа обьекта
                obj_type = []
                primech_pm = []
                bomNaimenovanie = bom['Наименование'].tolist()
                for num, x in enumerate(bomNaimenovanie):
                    if (x == '.'):
                        obj_type.append("2160")
                        primech_pm.append('Элемент печатного монтажа')
                    else:
                        obj_type.append("1138")
                        primech_pm.append(np.nan)
                bom['primech_pm'] = primech_pm
                primech_pm_ = []
                bomPrimechPm = bom['primech_pm'].tolist()
                for num, x in enumerate(bomPrimechPm):
                    if (bom['primech_pm'].iloc[num] == 'Элемент печатного монтажа'):
                        if (isinstance(bom['Примечания'].iloc[num], float)):
                            primech_pm_.append(bom['primech_pm'].iloc[num])
                        else:
                            primech_pm_.append(f"{bom['Примечания'].iloc[num]} {bom['primech_pm'].iloc[num]}")
                    else:
                        primech_pm_.append(bom['Примечания'].iloc[num])
                bom['Примечания'] = primech_pm_

                bom['Тип обьекта'] = obj_type
                bom['Класс'] = new_list_class
                bom['Фирма изготовитель'] = new_list_firm
                bom['Функциональное назначение'] = new_list_func
                bom['Примечание для производства'] = new_list_assembly_note
                bom['Примечание для производства'] = self.create_func(bom['Примечание для производства'].tolist(),
                                                                 bom['Примечание ПЭ'].tolist(), bom[Cadence_Name].tolist())
                bom['Вариант'] = np.array(var_idx).astype(int)
                bom['Обозначение'] = ['' for x in range(len(new_list_class))]
                bom['Элемент перечня элементов'] = ['' for x in range(len(new_list_class))]
                bom = bom[
                    ['Наименование', Cadence_Name, Ref, Count, 'Вариант', 'Примечание ПЭ', 'Примечания', 'Тип обьекта',
                     'Обозначение', 'Элемент перечня элементов', 'Класс', 'Фирма изготовитель', 'Функциональное назначение',
                     'Примечание для производства']]
                file_name = self.name_file.split("\\")[-1].split(".")[0]
                file_name_with_type = self.name_file.split("\\")[-1]
                print(file_name)
                path = self.name_file.replace(file_name_with_type, '')
                print(path)
                bom.to_excel(f'{path}intermech_{file_name}.xlsx', index=False, engine='openpyxl')
                print(f'\nСоздан загрузочный BOM файл для САПР Интермех: {path}intermech_{file_name}\n')
                end = datetime.datetime.now()
                print(end-start)
                return(True, f"{path}intermech_{file_name}.xlsx")
            except:
                return(False, 'Error')
        else:
            print('--------Вы не выбрали файл---------\n')

    ### Функции для работы с pickandplace
    def create_func(self, list0, list1, list2):
        obr_list = []
        for x, y, z in zip(list0, list1, list2):
            if ((str(x)) != 'nan'):
                obr_list.append(str(x).lstrip() + '_' + str(y))
            else:
                obr_list.append(str(z).lstrip() + '_' + str(y))
        return obr_list

    # pick_file
    # bom_file
    # zam_file

    def obr_nai_zam(self, x):
        x = x.split('(ф.')
        x = x[0]
        x = x.rstrip().lstrip()
        return x

    def convert_string(self, x):
        x = x.rstrip().lstrip().replace('✽', '')
        return x

    def convertpick(self, checkdbval, bom_file, pick_file, zam_file):
        print(checkdbval, bom_file, pick_file, zam_file)
        try:
            bom_file
            pick_file
        except:
            print(f'Выбраны не все файлы!!!\n')
        print(bom_file)

        pick = pd.read_csv(pick_file, sep='!', skiprows=[0, 1, 2])
        pick.columns = ['refdes', 'symbol_x', 'symbol_y', 'rotation', 'mirror', 'symbol_name', 'embedded_layer']
        pick = pick.drop([0])
        pick = pick[['refdes', 'symbol_x', 'symbol_y', 'rotation', 'mirror', 'symbol_name']]
        new_refdes = []
        for x in pick['refdes'].tolist():
            new_refdes.append(self.convert_string(x))
        pick['refdes'] = new_refdes

        if file_type == 'xlsx':
            bom = pd.read_excel(bom_file)
        elif file_type == 'html':
            bom = pd.read_html(bom_file)[1]
            bom.columns = bom.iloc[0]
            bom = bom.drop(0)
            bom = bom.drop(len(bom['Qty'].tolist()))
        else:
            print('Выбраный файл иммеет не верный формат!\n')

        new_refdes_ = []
        for x in bom['Ref Des'].tolist():
            new_refdes_.append(self.convert_string(x))
        bom['Ref Des'] = new_refdes_

        # Проверка на соответствие файлов
        for x in pick['refdes'].tolist():
            if x not in bom['Ref Des'].tolist():
                print(f'Элемент {x} присутствует в файле {pick_file}, но отсутствует в {bom_file}')
                print(f'Элемент {x} присутствует в файле {pick_file}, но отсутствует в {bom_file}\n')

        for x in bom['Ref Des'].tolist():
            if x not in pick['refdes'].tolist():
                print(f'Элемент {x} присутствует в файле {bom_file}, но отсутствует в {pick_file}')
                print(f'Элемент {x} присутствует в файле {bom_file}, но отсутствует в {pick_file}\n')

        # Ищем соответствие
        cadname_list = []
        for num, x in enumerate(pick['refdes'].tolist()):
            if (x in bom['Ref Des'].tolist()):
                for num1, y in enumerate(bom['Ref Des'].tolist()):
                    if (x == y):
                        cadname_list.append(bom['PART_NUMBER'].iloc[num1])
            else:
                cadname_list.append('-')

        try:
            pick['part_number'] = cadname_list
        except:
            print('\n')
            print('Файлы не могут быть обработаны, необходимо исправить замечания!!!\n')

        # Генерим ведомость замен если это необходимо
        try:
            zam = pd.read_excel(zam_file)
            zam_status = True
        except:
            zam_status = False

        zam_list = []
        if (zam_status):
            zam[zam.columns[1]] = zam[zam.columns[1]].apply(lambda x: self.obr_nai_zam(x))
            zam = zam.drop_duplicates(subset=[zam.columns[1], zam.columns[3]])
            if (~(pd.Series(zam[zam.columns[1]].tolist()).is_unique)):
                print(zam.columns)
                zam.dropna(subset=[zam.columns[1]])
                pick['part_number'] = pick['part_number'].replace('.', 'NC')
                zam['DUBL'] = (zam[zam.columns[1]]).duplicated()
                print(f"{zam[zam['DUBL'] == True][zam.columns[1]]} - Не уникальные наименования\n")
            for num_elem_zam, elem_zam in enumerate(pick['part_number'].tolist()):
                cikl = True
                sov = False
                for num_elem_zam1, elem_zam1 in enumerate((zam[zam.columns[1]]).tolist()):
                    if cikl:
                        try:
                            sovpod = re.findall(f"{elem_zam}", elem_zam1)
                            print(sovpod[0])
                            if (elem_zam != elem_zam1):
                                print(f"WARNING!!! {elem_zam} {elem_zam1} - Партномера совпадают не полностью!!!")
                                print(f"WARNING!!! {elem_zam} {elem_zam1} - Партномера совпадают не полностью!!!\n")
                            sov = True
                        except:
                            sov = False
                    if (sov):
                        zam_list.append(zam.iloc[num_elem_zam1][zam.columns[3]])

                        cikl = False
                        sov = False
                if (cikl):
                    zam_list.append("-")
            try:
                pick['replace'] = zam_list
            except:
                print(f"{zam[zam['DUBL'] == True][zam.columns[1]]} - не уникальное наименование в ведомости замен\n")
                pick['replace'] = zam_list

        # Если выбрана опция синхронизации с БД IMBASE
        if (checkdbval):
            Cadence_Name_list = self.base_intermech['Cadence_Name'].tolist()
            assembly_notes = []
            for x in pick['part_number'].tolist():
                if x in Cadence_Name_list:
                    for num, y in enumerate(Cadence_Name_list):
                        if (x == y):
                            assembly_notes.append(self.base_intermech['Примечание для производства'].iloc[num])
                else:
                    assembly_notes.append('-')

            pick['ass_note'] = assembly_notes
            pick['ass_note'] = self.create_func(pick['ass_note'].tolist(), pick['symbol_name'].tolist(),
                                                pick['part_number'].tolist())
            pick.to_excel(f'{folder}\{bom_file.split("/")[-1].split(".")[0]}_place.xlsx', index=False)
        else:
            ass_note = [np.nan for x in range(len(pick['symbol_name'].tolist()))]
            pick['ass_note'] = ass_note
            pick['ass_note'] = self.create_func(pick['ass_note'].tolist(), pick['symbol_name'].tolist(),
                                                pick['part_number'].tolist())
            pick.to_excel(f'{folder}\{bom_file.split("/")[-1].split(".")[0]}_place.xlsx', index=False)
        print(f'Файл создан!!!\n')


