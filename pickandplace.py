def create_func(self, list0, list1, list2):
	obr_list = []
	for x, y, z in zip(list0, list1, list2):
		if ((str(x)) != 'nan'):
			obr_list.append(str(x).lstrip()+'_'+ str(y))
		else:
			obr_list.append(str(z).lstrip()+'_'+ str(y))
	return obr_list

#pick_file
#bom_file
#zam_file


def obr_nai_zam(self, x):
	x = x.split('(ф.')
	x = x[0]
	x = x.rstrip().lstrip()
	return x

def convert_string(self, x):
	x = x.rstrip().lstrip().replace('✽', '')
	return x

def convert(self, checkdbval, bom_file, pick_file, zam_file=[]):
	try:
		bom_file
		pick_file
	except:
		print(f'Выбраны не все файлы!!!\n')
	print(bom_file)

	pick = pd.read_csv(pick_file, sep = '!', skiprows = [0, 1, 2])
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
		zam = zam.drop_duplicates(subset = [zam.columns[1], zam.columns[3]])
		if (~(pd.Series(zam[zam.columns[1]].tolist()).is_unique)):
			print(zam.columns)
			zam.dropna(subset=[zam.columns[1]])
			pick['part_number'] = pick['part_number'].replace('.', 'NC')
			zam['DUBL'] = (zam[zam.columns[1]]).duplicated()
			print(f"{zam[zam['DUBL']==True][zam.columns[1]]} - Не уникальные наименования\n")
		for num_elem_zam, elem_zam in enumerate(pick['part_number'].tolist()):
			cikl = True
			sov = False
			for num_elem_zam1, elem_zam1 in enumerate((zam[zam.columns[1]]).tolist()):
				if cikl:
					try:
						sovpod = re.findall(f"{elem_zam}", elem_zam1)
						print(sovpod[0])
						if(elem_zam != elem_zam1):
							print(f"WARNING!!! {elem_zam} {elem_zam1} - Партномера совпадают не полностью!!!")
							print(f"WARNING!!! {elem_zam} {elem_zam1} - Партномера совпадают не полностью!!!\n")
						sov = True
					except:
						sov = False
				if(sov):
					zam_list.append(zam.iloc[num_elem_zam1][zam.columns[3]])

					cikl = False
					sov = False
			if(cikl):
				zam_list.append("-")
		try:
			pick['replace'] = zam_list
		except:
			print(f"{zam[zam['DUBL']==True][zam.columns[1]]} - не уникальное наименование в ведомости замен\n")
			pick['replace'] = zam_list

	#Если выбрана опция синхронизации с БД IMBASE
	if(checkdbval):
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
		pick['ass_note'] = self.create_func(pick['ass_note'].tolist(), pick['symbol_name'].tolist(), pick['part_number'].tolist())
		pick.to_excel(f'{folder}\{bom_file.split("/")[-1].split(".")[0]}_place.xlsx', index = False)
	else:
		ass_note = [np.nan for x in range(len(pick['symbol_name'].tolist()))]
		pick['ass_note'] = ass_note
		pick['ass_note'] = self.create_func(pick['ass_note'].tolist(), pick['symbol_name'].tolist(),
									   pick['part_number'].tolist())
		pick.to_excel(f'{folder}\{bom_file.split("/")[-1].split(".")[0]}_place.xlsx', index=False)
	print(f'Файл создан!!!\n')