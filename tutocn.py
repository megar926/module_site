name = str(request.POST.get('DataInput'))
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
              'ТЕРМОДАТЧИК', 'КЛЕММА', 'РЕЛЕ', 'ФИЛЬТР ПОМЕХОПОДАВЛЯЮЩИЙ', 'ТЕРМОРЕЗИСТОР']

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
if ((cadence != 'NONE') and (cadence != '')):
    today = datetime.datetime.today()
    b = InputData(tuname=f'{name}', caname=f'{cadence}', date=today.strftime("%Y-%m-%d %H:%M:%S"))
    b.save()

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

# if cadence in data['Cadence_Name'].to_list():
#    sost='Элемент присутствует в базе Интермех'
# elif (f'{cadence}0' in data['Cadence_Name'].to_list()):
#    sost='Элемент присутствует в базе Интермех!!!'
# else:
#    sost='Элемент отсутствует в базе Интермех!!!'

try:
    mydb = mysql.connector.connect(
        host="server224.hosting.reg.ru",
        user="u1051830_alexand",
        password="Megare926",
        port="3306",
        db="u1051830_cadence_name")

    mycursor = mydb.cursor()
    # mycursor.execute(f"INSERT INTO cadence_name_query VALUES ('{datetime.datetime.now()}', '{name}', '{cadence}')")
    # mydb.commit()

    mycursor.execute(f"SELECT name FROM intermech_base WHERE cadence_name = '{cadence}'")
    select_data = []
    for x in mycursor:
        select_data.append(x[0])
    if len(select_data) > 0:
        sost = f"Элемент {select_data[0]} присутствует в базе IMbase!"
    else:
        mycursor.execute(f"SELECT name FROM intermech_base WHERE name = '{name}'")
        select_data = []
        for x in mycursor:
            select_data.append(x[0])
        if len(select_data) > 0:
            sost = f"Элемент {select_data[0]} присутствует в базе IMbase!"
        else:
            sost = 'Элемент отсутствует в базе IMbase!!!'
            mycursor.execute(
                f"INSERT INTO cadence_name_query VALUES ('{datetime.datetime.now()}', '{name}', '{cadence}')")
            mydb.commit()
            if name != 'NONE':
                bot.send_message("260945403", name)
except:
    pass

# sost = 'DB empty'
date = {'cadence': cadence + color, 'tuname': name, 'url_download': now_name, 'inte': sost, 'status': status}
context = {'info': date}
return render(request, 'intermech_main/index.html', context)