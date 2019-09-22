# USchedule
Скачивание и переработка расписания ИМИ указанной группы в удобный для глаз формат

NOTE: В будущем предусматривается создание интерфейса для мобильных устройств

Программа скачивает с сайта ( *https://www.s-vfu.ru/universitet/rukovodstvo-i-struktura/instituty/imi/uchebnyy-protsess* ) последнее вышедшее расписание путем парсинга и поиска по ключевому словосочетанию "Расписание ИМИ".
Далее с помощью библиотеки xlrd открывает рабочую страницу, указанную в переменной `sheet_name`, находит там группу, указанную в переменной `group` и приступает к созданию словарика, состоящего из элементов:
	1. Группа, для которой создано расписание
	2. Расписание предметов для каждого из 6 рабочих дней, состоящее конкретно из: времени, названия предмета, аудитории, типа занятия(пр., лаб., лек.) - все согласно эксель файлу
Далее из данного словарика формируются JSON-файл для души и TXT-файл для комфортного просмотра на используемом устройстве. На телефоне TXT-файл можно открыть word'ом, а если таковой отсутствует, м

Пример того, как могут выглядеть эти файлы при значении переменных `sheet_name="2 курс _ИТ"`(в названии рабочего листа в эксель файле на момент написания этого текста стоял пробел, потому он имеется и здесь - значение этой переменной должно строго соответствовать названию необходимой рабочей страницы) и `group="фиит-18"`(капсом или нет - не важно, главное, чтобы не было ошибок):

1. **JSON**

`
	{
	"Расписание для": "2 курс _ИТ БА-ФИИТ-18 (22 студентов)",
	"Понедельник": [
		"8.00 - 9.35 -",
		"9.50 - 11.25 Безопасность жизнедеятельности* Софронов Р.П. /Операционные системы** Павлов А.В.   Ауд. 263 326 л",
		"11.40 - 13.15 Операционные системы* (1/2), **(1/2) Павлов А.В.   Ауд. 430 лаб",
		"14.00 - 15.35 Иностранный язык Алексеева Н.Н. -728, Протопопова Т.А. - 445, Тарекегн Мусе -324, Ядрихинская Е.Е. -447, Сидорова Л.В.-326, Ноговицына О.С. -449, Татаринова А.В.-330, Ермолаева Т.К.-349, Максимов А.А. 451 Федорова А.Я. -457   Ауд.  ",
		"15.50 - 17.25 -",
		"17.40 - 19.15 -"
	],
		...
	}
`

2. **TXT**

`
	Расписание для: 2 курс _ИТ БА-ФИИТ-18 (22 студентов)
``
	Понедельник:
		8.00 - 9.35 -
		9.50 - 11.25 Безопасность жизнедеятельности* Софронов Р.П. /Операционные системы** Павлов А.В.   Ауд. 263 326 л
		11.40 - 13.15 Операционные системы* (1/2), **(1/2) Павлов А.В.   Ауд. 430 лаб
		14.00 - 15.35 Иностранный язык Алексеева Н.Н. -728, Протопопова Т.А. - 445, Тарекегн Мусе -324, Ядрихинская Е.Е. -447, Сидорова Л.В.-326, Ноговицына О.С. -449, Татаринова А.В.-330, Ермолаева Т.К.-349, Максимов А.А. 451 Федорова А.Я. -457   Ауд.  
		15.50 - 17.25 -
		17.40 - 19.15 -
``
	...
`