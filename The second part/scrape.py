import os
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup

#skripta predpostavlja da se results folder nalazi u istom direktorijumu kao i skripta
#poseban folder za insurance csv
#try catch?
def re_clean(exp, string_content):
    re_clean = re.sub(exp, ' ', string_content).strip()
    return re_clean

def rowloop(table):
    temp = []
    rows = table.findChildren("td")
    for r in rows:
        cell_content = r.getText()
        if cell_content == '\xa0':
            clean_content = re_clean('\xa0', cell_content)
        if cell_content == '\n':
            clean_content = re_clean('\n', cell_content)
        clean_content = re_clean('\s+', cell_content)
        temp.append(clean_content)
    return temp

def parsehtml(apcant_id):
    values = []
    index = 0
    base_url = "https://li-public.fmcsa.dot.gov/LIVIEW/pkg_carrquery.prc_activeinsurance?pv_apcant_id="#testing
    url = base_url + str(apcant_id)
    html = requests.get(url)
    soup = BeautifulSoup(html.text, "lxml")
    table = soup.findChildren("table")[4]
    form_header = table.findChildren("th", headers="form")
    if len(form_header) == 0:
        values = []
        return values
    values = rowloop(table)
    for t in form_header:
        header_content = t.getText()
        clean_header = re_clean('\s+', header_content)
        values.insert(index, header_content)
        index = index + 9
    s = 'BIPD/Primary'
    pos = values.index(s) if s in values else -1
    actual_values = values[pos-1:pos+8] #since we need just the row with BIPD/Primary
    return actual_values

def save_csv(dirname, csv, csvname):
    if os.path.isdir(dirname):
        csv.to_csv(os.path.join(dirname, csvname), index=False)
    else:
        os.mkdir(dirname)
        csv.to_csv(os.path.join(dirname, csvname), index=False)

base_dir = os.path.dirname('C:/LuckyTruck/')
#base_dir = os.getcwd()
csv_dir = os.path.join(base_dir, 'results')

for f in os.listdir(csv_dir):
    if f.endswith(".csv"):
        fname = os.path.join(csv_dir,f)
        csv = pd.read_csv(fname)
        csvname = f.split('.')
        number =  int(csvname[0][-1])
        emptydot = csv[csv["USDOT Number"].isnull()]
        emptydotname = "empty" + str(number) + ".csv"
        emptydotdir = os.path.join(base_dir, "empty")
        save_csv(emptydotdir, emptydot, emptydotname)
        csv.dropna(subset=['USDOT Number'], inplace=True)

        insurance_headers = ['pv_apcant_id','Form','Type','Insurance Carrier','Policy/Surety','Posted Date','Coverage From','Coverage To','Effective Date','Cancellation Date']
        icsv = pd.DataFrame(columns=insurance_headers)
        ids = csv['pv_apcant_id'].values

        for apcant_id in ids:
            values = []
            values.append(apcant_id)
            parsed_insurance = parsehtml(apcant_id)
            if not parsed_insurance:
                empty = ['']*10
                empty[0] = values[0]
                icsv = icsv.append(pd.Series(empty,index=insurance_headers), ignore_index=True)
            else:
                values.extend(parsed_insurance)
                icsv = icsv.append(pd.Series(values, index=insurance_headers), ignore_index=True)

        icsv['pv_apcant_id'] = icsv['pv_apcant_id'].astype(int)
        #icsv['Effective Date'].fillna('No Data Available', inplace=True)
        number =  int(csvname[0][-1])
        icsvname = "insurance" + str(number) + ".csv"
        icsv_dir = os.path.join(base_dir, 'insurance')
        save_csv(icsv_dir, icsv, icsvname)

        new = pd.merge(csv, icsv, on=['pv_apcant_id'])
        new['USDOT Number'] = new['USDOT Number'].astype(int)
        del new['pv_apcant_id']

        old_headers = ['USDOT Number','Legal Name','DBA Name','Form','Type','Insurance Carrier','Policy/Surety','Posted Date','Coverage From','Coverage To','Effective Date','Cancellation Date']
        new_headers = ['DOT_NUMBER', 'Name', 'DBA Name', 'Insurance Form', 'Insurance Type', 'Insurance Carrier', 'Insurance Policy/Surety', 'Insurance Posted Date', 'Insurance Coverage From', 'Insurance Coverage To', 'Insurance Effective Date', 'Insurance Cancellation Date']
        replacement = dict(zip(old_headers,new_headers))
        new = new.rename(columns=replacement)
        luckycsv1 = pd.read_csv(os.path.join(base_dir,"CompanyID_USDOTNumber_Association_LuckyTruck1.csv"))
        luckycsv2 = pd.read_csv(os.path.join(base_dir,"CompanyID_USDOTNumber_Association_LuckyTruck2.csv"))
        del luckycsv1['Name']
        del luckycsv2['Name']

        n1 = pd.merge(luckycsv1, new, on=['DOT_NUMBER'])
        n2 = pd.merge(luckycsv2, new, on=['DOT_NUMBER'])

        n1name  = "merged" + str(number) + "-1" + ".csv"
        n2name  = "merged" + str(number) + "-2" + ".csv"

        unmatched1 = pd.merge(luckycsv1, new, on=['DOT_NUMBER'], how='right')
        unmatched2 = pd.merge(luckycsv2, new, on=['DOT_NUMBER'], how='right')

        unmatchedname = "unmatched" + str(number)  + ".csv"

        unmatched1 = unmatched1[unmatched1['Company ID'].isnull()]
        unmatched2 = unmatched2[unmatched2['Company ID'].isnull()]
        unmatched1['Company ID'].fillna(value='No Data Available', inplace=True)
        unmatched2['Company ID'].fillna(value='No Data Available', inplace=True)

        unmatchedfinal = pd.merge(unmatched1,unmatched2)
        unmatched_dir = os.path.join(base_dir,'unmatched')
        save_csv(unmatched_dir, unmatchedfinal, unmatchedname)

        mcsv_dir = os.path.join(base_dir,'merged')
        save_csv(mcsv_dir, n1, n1name)
        save_csv(mcsv_dir, n2, n2name)

        wtfname1 = mcsv_dir+"/"+n1name
        wtfname2 = mcsv_dir+"/"+n2name
        wtf1 = pd.read_csv(wtfname1)
        wtf2 = pd.read_csv(wtfname2)
        wtf1['Insurance Effective Date'].fillna(value='No Data Available', inplace=True)
        wtf2['Insurance Effective Date'].fillna(value='No Data Available', inplace=True)

        save_csv(mcsv_dir, wtf1, n1name)
        save_csv(mcsv_dir, wtf2, n2name)
    else:
        continue

