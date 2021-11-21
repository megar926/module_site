import re

def convert(in_data):
    name = str(in_data)
    name = name.upper()
    name = name.replace('ТУ/Д1', 'ТУ')
    no_sym_list = ['-', '+', '–', '%', ' ', '±', '«', '»', '.', '"', '/', '\\', '*', '#', '‑']
    alf_dict = {'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'JO',
                'Ж': 'ZH', 'З': 'ZH', 'И': 'I', 'Й': 'JJ', 'К': 'K', 'Л': 'L', 'У': 'U', 'Р': 'R', 'О': 'O', 'М': 'M',
                'И': 'I', 'Н': 'N', 'Т': 'T',
                'Ф': 'F', "Х": "KH", 'Ц': 'C', 'Ч': 'CH', 'Ш': 'SH', 'Щ': 'SHH', 'Ы': 'Y', 'Э': 'EH',
                'Ю': 'JU', 'Я': 'JA', 'П': 'P', 'С': 'S'}
    class_elem = ['МИКРОСХЕМА', 'РЕЗИСТОР', 'КОНДЕНСАТОР', 'ТРАНЗИСТОР', 'ДИОД', 'РЕЗИСТОРНАЯ СБОРКА', 'ТРАНСФОРМАТОР',
                  'ДРОССЕЛЬ',
                  'БЛОК ТРАНСФОРМАТОРОВ', 'СБОРКА ТРАНЗИСТОРНАЯ', 'ТРАНЗИСТОРНАЯ СБОРКА', 'СТАБИЛИТРОН', 'ПРЕДОХРАНИТЕЛЬ',
                  'ТЕРМОДАТЧИК', 'КЛЕММА', 'РЕЛЕ', 'ФИЛЬТР ПОМЕХОПОДАВЛЯЮЩИЙ', 'ТЕРМОРЕЗИСТОР', 'МИКРОСБОРКА']

    for x in class_elem:
        if x in name:
            name = name.replace(x, '')

    tu = re.search(r'\w+[.]\d+[.]\d+[' ']*ТУ[\w,\s,-]*', name)
    if (tu):
        tu = re.search(r'\w+[.]\d+[.]\d+[' ']*ТУ[\w,\s,-]*', name).group()
    else:
        tu = ''

    name_ic = name.replace(tu, '')

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
    cadence = cadence.replace(' ', '')
    cadence = cadence.replace('-Р', '')

    er0 = re.findall(r'\d[,]\w', cadence)
    er1 = re.findall(r'\w[,]\w', cadence)
    for x in list(cadence):
        if x in alf_dict.keys():
            er2 = True
        else:
            er2 = False
    er3 = re.findall(r'\w[,]', cadence)
    er4 = re.findall(r'\d[,]', cadence)
    if (er0 or er1 or (er2 == True) or er3 or er4):
        color = '-----> Возможна ошибка в наименовании!!! Будьте внимательнее! <-----'
    else:
        color = ''

    return cadence+color

print(convert('Микросборка р1-8мп 8908.908 ТУ'))