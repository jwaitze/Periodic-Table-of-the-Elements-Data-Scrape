import requests, time, openpyxl
from bs4 import BeautifulSoup

def ScrapeTableOfElements():
    url = 'http://www.lenntech.com/periodic-chart-elements/atomic-number.htm'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    tables = soup.find_all('table')
    tbodys = tables[0].find_all('tbody')
    trs = tbodys[0].find_all('tr')
    elements = []
    for tr in trs:
        tds = tr.find_all('td')
        element = []
        for td in tds:
            if ' ' not in td.text and len(td.text) <= 12 and len(td.text) >= 1 and ',' not in td.text and '-' not in td.text:
                element.append(td.text)
        if len(element) == 3:
            elements.append(element)
            print(element)
    print()
    return elements

def GetElementDataFromWikipedia(element):
    element_data = []
    url = 'https://en.wikipedia.org/wiki/' + element
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    infoboxes = soup.find_all('table', 'infobox')
    trs = infoboxes[0].find_all('tr')
    for tr in trs:
        ths = tr.find_all('th')
        tds = tr.find_all('td')
        try:
            if len(ths[0].text) > 0 and len(tds[0].text) > 0:
                element_data.append([ths[0].text, tds[0].text])
        except:
            pass
    return element_data

def ScrapeAllElementsData():
    elements = ScrapeTableOfElements()
    details = []
    elements_data = []
    for element in elements:
        try:
            element_data = GetElementDataFromWikipedia(element[1])
            for detail in element_data:
                if detail[0] not in details:
                    details.append(detail[0])
            elements_data.append(element_data)
        except:
            try:
                element_data = GetElementDataFromWikipedia(element[1] + '_(element)')
                for detail in element_data:
                    if detail[0] not in details:
                        details.append(detail[0])
                elements_data.append(element_data)
            except:
                continue
        print(element[0], element[1], element[2], '|', str(len(elements_data[-1])), 'details')
        for row in elements_data[-1]:
            print(row)
        print()
        print(str(len(details)), 'unique details', '|', str(round( 100*( int(element[0]) / 118 ), 3) ) + '% done')
        print()
        #time.sleep(1)
    return [elements, details, elements_data]

if __name__ == '__main__':
    elements, details, elements_data = ScrapeAllElementsData()
    wb = openpyxl.Workbook()
    ws = wb.worksheets[0]
    for d in range(len(details)):
        ws.cell(row=1, column=1+3+d).value = details[d]
    for e in range(len(elements)):
        for d in range(3):
            ws.cell(row=1+1+e, column=1+d).value = elements[e][d]
    for e in range(len(elements_data)):
        for d in range(len(elements_data[e])):
            i = details.index(elements_data[e][d][0])
            ws.cell(row=1+1+e, column=1+3+i).value = elements_data[e][d][1]
    wb.save('periodic_table.xlsx')
