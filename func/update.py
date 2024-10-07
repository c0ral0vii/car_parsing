from openpyxl import load_workbook


async def update_excel(data: list):
    '''
    Дополнение excel-файла
    '''

    wb = load_workbook(filename='output/cars.xlsx', data_only=True)
    ws = wb.active

    ws.append(data)
    wb.save('output/cars.xlsx')