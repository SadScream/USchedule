import re
import requests
import bs4 as bs
import xlrd


url = "https://www.s-vfu.ru/universitet/rukovodstvo-i-struktura/instituty/imi/uchebnyy-protsess/"


class Document:

    def __init__(self):
        self.url = url
        self.soup = self.open_soup()
        content = self.content_searcher()
        print(content)
        self.document = self.get_document(content)

    def open_soup(self):
        response = requests.get(self.url).content
        soup = bs.BeautifulSoup(response, 'lxml')
        return soup

    def content_searcher(self):
        content = self.soup.find("div", id="content")
        return "https://www.s-vfu.ru"+str(content.find_all("a")[0].get('href'))

    def get_document(self, url):
        r = requests.get(url, stream=True)
        path = "C:\\Users\\Илья\Desktop\\table.xls"

        with open(path, "wb") as out:
            for chunk in r.iter_content(512):
                out.write(chunk)

        return path


class ParseDocument(Document):

    def __init__(self):
        super().__init__()
        self.file = self.document
        self.open_excel()

    def open_excel(self):
        rb = xlrd.open_workbook(self.file, formatting_info=True)
        sheet = rb.sheet_by_name("1 курс_ИТ")
        column=14
        table = []

        for col in range(sheet.ncols):
            if "ИВТ-19-3" in sheet.cell_value(2,col):
                column = col

        days = []
        d = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота"]
        tbl = {'Понедельник': [], 'Вторник': [], 'Среда': [], 'Четверг': [], 'Пятница': [], 'Суббота': []}
        for row in range(3,sheet.nrows):
            if len(sheet.cell_value(row,0)):
                if sheet.cell_value(row,0).lower() in d:
                    days.append(sheet.cell_value(row,0).lower())

            v = sheet.cell_value(row,column)
            if not(len(v)):
                if len(sheet.cell_value(row,column+1)):
                    for i in range(1, sheet.ncols):
                        if len(sheet.cell_value(row,column-i)):
                            v = sheet.cell_value(row,column-i)
                            break

            tbl[days[-1].title()].append(f"{v}   Ауд. {sheet.cell_value(row,column+2)}")

                

        print(tbl)




if __name__ == '__main__':
    ParseDocument()