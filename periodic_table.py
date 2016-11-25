# Periodic Table of the Elements Scrape
# Excel Workbook & JSON Database output
# Utilizes lenntech.com and wikipedia.org for data

# Written by Jake Waitze
# Contact: Jake@Waitze.net

filename_prefix = 'periodic_table'
strip_extraneous_characters = True

import sys, requests, time, openpyxl
from bs4 import BeautifulSoup

start_time = time.time()

def scrape_table_of_elements():
    def is_wanted_lenntech_table_data(data):
        if ' ' in data or ',' in data or '-' in data:
            return False
        if len(data) <= 12 and len(data) >= 1:
            return True
        return False
    url = 'http://www.lenntech.com/periodic-chart-elements/atomic-number.htm'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    tables = soup.find_all('table')
    tbodys = tables[0].find_all('tbody')
    trs = tbodys[0].find_all('tr')
    elements = []
    for tr in trs:
        tds = tr.find_all('td')
        element = [td.text for td in tds if is_wanted_lenntech_table_data(td.text)]
        if len(element) == 3:
            element[0] = int(element[0])
            elements.append(element)
            print(element)
    print()
    return elements

def process_raw_wikipedia_table(detail):
    body = detail[1].replace('\xa0', ' ').replace('\u200b', '').strip()
    title = detail[0].lower().replace(', ', '_').replace('\xa0', ' ')
    title = title.replace(' ', '_').replace('.', '').strip()
    title = title.replace('\'', '').replace('\n', '')
    for i in range(1, 25):
        title = title.replace('[' + str(i) + ']', '')
        body = body.replace('[' + str(i) + ']', '')
    if body.replace('-', '').replace('.', '').isdigit() and '-' not in body[1:] and body.count('.') < 2:
        if '.' in body:
            body = float(body)
        else:
            body = int(body)
    extraneous_delimeters = ']) '
    if strip_extraneous_characters and type(body) is str and sum([1 for e in extraneous_delimeters if e in body]) != 0:
        stripped = body
        for e in extraneous_delimeters:
            if e in stripped:
                stripped = stripped[:stripped.index(e)]
        strip_chars = '[(,' + extraneous_delimeters
        for c in strip_chars:
            stripped = stripped.replace(c, '')
        if stripped.replace('.', '').replace('-', '').isdigit() and '-' not in stripped[1:] and stripped.count('.') < 2:
            if '.' in stripped:
                body = float(stripped)
            else:
                body = int(stripped)
    if type(body) is str:
        split_delimeters = [', ', '\n']
        for s in split_delimeters:
            if s in body:
                body = body.split(s)
                body = [d for d in body if len(d) != 0 and d != ' ']
    if 'atomic_number' in title:
        title = 'atomic_number'
    elif 'standard_atomic_weight' in title:
        title = 'atomic_weight'
    elif 'density_at_stp' in title:
        title = 'density_at_stp'
    elif 'period' == title:
        body = int(body[body.index(' ')+1:])
    if type(body) is list:
        body = ', '.join(body)
    return title, body

def get_element_data_from_wikipedia(element):
    element_data = []
    url = 'https://en.wikipedia.org/wiki/%s' % element
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
        detail[0], detail[1] = process_raw_wikipedia_table(detail)
    return element_data

def scrape_all_elements_data():
    elements = scrape_table_of_elements()
    details, elements_data, element_data = [], [], []
    for element in elements:
        print('Scraping ' + element[1] + '...')
        try:
            element_data = get_element_data_from_wikipedia(element[1])
        except:
            try:
                element_data = get_element_data_from_wikipedia(element[1] + '_(element)')
            except:
                continue
        for detail in element_data:
            if detail[0] not in details:
                details.append(detail[0])
        elements_data.append(element_data)
        print(element[0], element[1], element[2], '|', str(len(elements_data[-1])), 'details')
        [print(row) for row in elements_data[-1]]
        print()
        done_percentage = round(100*( int(element[0])/118 ), 1)
        time_elapsed = round(time.time() - start_time, 1)
        estimated_total_time = round((time_elapsed*100)/done_percentage, 1)
        seconds_done_str = str(time_elapsed) + ' / ~' + str(estimated_total_time) + ' secs elapsed'
        print(str(len(details)), 'unique details', '|', str(done_percentage) + '% done |', seconds_done_str)
        print()
        #time.sleep(1)
    return [elements, details, elements_data]

def write_elements_data_to_excel_workbook(filepath, elements, details, elements_data):
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
        ws.cell(row=1, column=1+c).value = ['number', 'name', 'symbol'][c]
    ws.freeze_panes = ws['D2']
    wb.save(filepath)

def excel_workbook_to_list(filepath):
    if '.xlsx' not in filepath:
        return []
    retval = []
    wb = openpyxl.load_workbook(filepath)
    ws = wb.worksheets[0]
    for row in ws.iter_rows():
        retval.append([cell.value for cell in row])
    return retval

def get_json_from_excel_workbook(filepath):
    excel_data = excel_workbook_to_list(filepath)
    keys, j = excel_data[0], []
    for row in range(1, len(excel_data)):
        j.append({})
        for k in range(len(keys)):
            if excel_data[row][k] == None:
                excel_data[row][k] = 'n/a'
            j[-1].update( { keys[k] : excel_data[row][k] } )
    return j

def write_json_list_to_file(filepath, j):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        for row in j:
            outfile.write(str(row) + '\n')

def write_elements_to_json_file(excel_filepath, json_filepath):
    j = get_json_from_excel_workbook(excel_filepath)
    write_json_list_to_file(json_filepath, j)

if __name__ == '__main__':
    try:
        start_time = time.time()
        elements, details, elements_data = scrape_all_elements_data()
        time_elapsed = round(time.time() - start_time, 1)
        if len(elements) == len(elements_data):# and len(elements) == 117:
            write_elements_data_to_excel_workbook(filename_prefix + '.xlsx', elements, details, elements_data)
            write_elements_to_json_file(filename_prefix + '.xlsx', filename_prefix + '.json')
            print('Wrote data to ' + filename_prefix + ' file.', str(time_elapsed), 'secs elapsed')
        else:
            print('Incorrect data retrieved. No output file written.', str(time_elapsed), 'secs elapsed')
    except:
        print('Error: Exception occured') # remove blanket exception for development/debugging
