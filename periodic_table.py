import sys, requests, time, openpyxl
from bs4 import BeautifulSoup

start_time = time.time()

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
            element[0] = int(element[0])
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
    for detail in element_data:
        if detail[0] == 'Atomic number (Z)':
            detail[1] = int(detail[1])
    return element_data

def ScrapeAllElementsData():
    elements = ScrapeTableOfElements()
    details = []
    elements_data = []
    for element in elements:
        print('Scraping ' + element[1] + '...')
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
        done_percentage = round(100*( int(element[0])/118 ), 1)
        time_elapsed = round(time.time() - start_time, 1)
        estimated_total_time = round((time_elapsed*100)/done_percentage, 1)
        seconds_done_str = str(time_elapsed) + ' / ~' + str(estimated_total_time) + ' secs elapsed'
        print(str(len(details)), 'unique details', '|', str(done_percentage) + '% done | ' + seconds_done_str)
        print()
        #time.sleep(1)
    return [elements, details, elements_data]

def WriteElementsDataToExcelWorkbook(elements, details, elements_data):
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
    for c in range(3):
        ws.cell(row=1, column=1+c).value = ['Number', 'Name', 'Symbol'][c]
    ws.freeze_panes = ws['D2']
    wb.save('periodic_table.xlsx')

if __name__ == '__main__':
    start_time = time.time()
    elements, details, elements_data = ScrapeAllElementsData()
    time_elapsed = round(time.time() - start_time, 1)
    if len(elements) == len(elements_data):# and len(elements) == 117:
        WriteElementsDataToExcelWorkbook(elements, details, elements_data)
        print('Wrote data to periodic_table.xlsx. ' + str(time_elapsed) + ' secs elapsed')
    else:
        print('Incorrect data retrieved. No output file written. ' + str(time_elapsed) + ' secs elapsed')
