import os
from bs4 import BeautifulSoup

pv_apcant_id = []
usdot_number = []
legal_name = []
dba_name = []

try:
    directory = os.listdir('C:/LuckyTruck/html')
    number_files = len(directory)
    for file in range(1, number_files+1, 1):
        data = open('C:/LuckyTruck/html/' + str(file) + '.html', 'rt').read()
        soup = BeautifulSoup(data, "lxml")
        # print(data)

        for a in soup.find_all('input'):
            listInputs = str(a).split()
            # print(listInputs)
            if listInputs[1][6:18] == 'pv_apcant_id':
                string = listInputs[3]
                id = ''
                for num in string:
                    if (num in "0123456789"):
                        id += num
                pv_apcant_id.append(id)

        # print(pv_apcant_id)

        for u in soup.find_all('td'):
            if (str(u)[13:25] == 'usdot_number'):
                # print(u)
                if (str(u)[28:34] == 'center'):
                    usdot = ''
                    result = str(u)[75:85]
                    for i in result:
                        if (i in "0123456789"):
                            usdot += i
                    usdot_number.append(usdot)
                else:
                    usdot_number.append('')
            if (str(u)[13:23] == 'legal_name'):
                # print(u)
                if (str(u)[26:32] == 'center'):
                    name = ''
                    result2 = str(u)[73:]
                    for j in range(0, len(result2), 1):
                        if (result2[j] + result2[j + 1] + result2[j + 2] != '</f'):
                            if (result2[j] == ';'):
                                name = name[:-3]
                            elif (result2[j] != ',' and result2[j] != '.'):
                                name += result2[j]
                        else:
                            break
                    legal_name.append(name)
                else:
                    legal_name.append('')
            if (str(u)[13:21] == 'dba_name'):
                # print(u)
                if (str(u)[24:30] == 'center'):
                    dba = ''
                    result3 = str(u)[71:]
                    for k in range(0, len(result3), 1):
                        if (result3[k] + result3[k + 1] + result3[k + 2] != '</f'):
                            if (result3[k] == ';'):
                                dba = dba[:-3]
                            elif (result3[k] != ',' and result3[k] != '.'):
                                dba += result3[k]
                        else:
                            break
                    dba_name.append(dba)
                else:
                    dba_name.append('')

        # print(usdot_number)
        # print(legal_name)
        # print(dba_name)

        csv_file = open('C:/LuckyTruck/results/data' + str(file) + '.csv', 'w', encoding='utf-8')
        csv_file.write('USDOT Number,Legal Name,DBA Name,pv_apcant_id')
        csv_file.write('\n')

        for row in range(0, len(pv_apcant_id), 1):
            csv_file.write(
                usdot_number[row] + "," + legal_name[row] + "," + dba_name[row] + "," + pv_apcant_id[row] + "\n")

        print(str(file) + '.html is DONE!')

        pv_apcant_id = []
        usdot_number = []
        legal_name = []
        dba_name = []
except Exception as e:
    # print(str(e))
    print('Error!')

print('-----------------')
print('All is DONE!')
input()