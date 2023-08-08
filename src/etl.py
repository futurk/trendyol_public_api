import requests
import hashlib
import os
import re
import sqlite3
import json
from pypdf import PdfReader
from dateutil.parser import parse as parsedate
from dateutil.tz import gettz

def get_remote_file_data(url: str):
    response = requests.get(url)
    if response.status_code == 200:
        date = response.headers.get('Last-Modified')
        content = response.content
        content_hash = hashlib.sha256(content).hexdigest()
        return content_hash, date
    else:
        return None

def download_file(url: str, path: str):
    response = requests.get(url)
    if response.status_code == 200:
        with open(path, 'wb') as file:
            file.write(response.content)
        print(f"File downloaded and saved in {path}")
    else:
        print(f"Failed to download file from {url}")

def parse_file(filepath: str):
    reader = PdfReader(filepath)
    text = ""
    for p in reader.pages:
        text += p.extract_text()
    #print(text)
    matches = re.findall(r'\d+,\d{2}', text) # "d+,dd" formatına uyanları bul 
    grouped_matches = [matches[i:i + 11] for i in range(0, len(matches), 11)] # 11'li gruplara ayır
    grouped_matches = grouped_matches[:101] # çünkü pdf'te 101. satır itibariyle boş hücreler kendini gösteriyor
    for i in range(len(grouped_matches)):
        # regex, ilk elemanda kusurlu sonuç doğurdu. desiyi ayırmak gerekli.
        grouped_matches[i][0] = grouped_matches[i][0][len(str(i)):]
        grouped_matches[i].insert(0, i)
    return grouped_matches

def save(shipping_costs, filedate):
    # array to db
    conn = sqlite3.connect('data/shipping_costs.db')
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS shipping_costs")
    cursor.execute('''
        CREATE TABLE shipping_costs (
            desi INTEGER PRIMARY KEY,
            aras REAL,
            mng REAL,
            ptt REAL,
            sendeo REAL,
            surat REAL,
            tex REAL,
            ups REAL,
            yurtici REAL,
            borusan REAL,
            ceva REAL,
            horoz REAL
        )
    ''')
    cursor.executemany('INSERT INTO shipping_costs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', shipping_costs)
    conn.commit()

    # db to json
    cursor.execute('SELECT * FROM shipping_costs')
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    response_data = {}
    for idx, row in enumerate(rows):
        row_data = {}
        for col_idx, col_name in enumerate(columns):
            row_data[col_name] = row[col_idx]
        response_data[str(idx)] = row_data
    response_data['last_changed'] = filedate
    with open("data/shipping_costs.json", "w") as outfile:
        json.dump(response_data, outfile)

    conn.close()

def main():
    url = 'https://tymp.mncdn.com/prod/documents/engagement/kargo/guncel_kargo_fiyatlari.pdf'
    local_filepath = 'data/guncel_kargo_fiyatlari.pdf'

    remote_filehash, remote_filedate = get_remote_file_data(url)
    # convert the format from "Tue, 01 Aug 2023 06:48:39 GMT" to "YYYY-MM-DD 09:48:39 +0300"
    remote_filedate = parsedate(remote_filedate).astimezone(gettz('Asia/Istanbul')).strftime("%Y-%m-%d %H:%M:%S %z")

    if os.path.exists(local_filepath):
        local_filehash = hashlib.sha256(open(local_filepath, 'rb').read()).hexdigest()
        if remote_filehash and remote_filehash == local_filehash:
            print("File is already up to date. No need to download.")
            return 0
        
    download_file(url, local_filepath)
    shipping_costs = parse_file(local_filepath)
    save(shipping_costs, remote_filedate)

if __name__ == '__main__':
    main()
