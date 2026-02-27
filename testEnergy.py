from energyCalculator import energyCalculator

import win32com.client

excel = win32com.client.GetActiveObject("Excel.Application")
workbookData = []
worksheets = []

for wb in excel.Workbooks:
    workbookData.append({
        "name": wb.name,
        "worksheets": [(ws.name,ws) for ws in wb.Worksheets]
    })
    worksheets = worksheets = [(ws.name,ws) for ws in wb.Worksheets]

usedWorksheet = None
#wsName = "5.3uh 1500A low"
wsName = "fil 80cm desat 850V low"
for name, ws in worksheets:
    if name == wsName:
        usedWorksheet = ws

print(usedWorksheet.Range("A1").Value)

time = [float(i[0]) for i in usedWorksheet.Range("A2:A10001").Value]
vds = [float(i[0]) for i in usedWorksheet.Range("C2:C10001").Value]
isw = [float(i[0]) for i in usedWorksheet.Range("F2:F10001").Value]

#plt.plot(time,vds)

energyCalc = energyCalculator()

energyCalc.integrateEdge(time,vds,isw)
print(energyCalc.result)