import requests
import hashlib
import os
import re
import sqlite3
import json
from PyPDF2 import PdfReader

def get_remote_file_hash(url):
    response = requests.get(url)
    if response.status_code == 200:
        content = response.content
        content_hash = hashlib.sha256(content).hexdigest()
        return content_hash
    else:
        return None

def download_file(url, local_filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(local_filename, 'wb') as file:
            file.write(response.content)
        print(f"File downloaded and saved as {local_filename}")
    else:
        print(f"Failed to download file from {url}")

def parse_file(local_filename):
    reader = PdfReader(local_filename)
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

def save(shipping_costs):
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
    with open("data/shipping_costs.json", "w") as outfile:
        json.dump(response_data, outfile)

    conn.close()

def main():
    url = 'https://tymp.mncdn.com/prod/documents/engagement/kargo/guncel_kargo_fiyatlari.pdf'
    local_filename = 'data/guncel_kargo_fiyatlari.pdf'

    remote_file_hash = get_remote_file_hash(url)

    if os.path.exists(local_filename):
        local_file_hash = hashlib.sha256(open(local_filename, 'rb').read()).hexdigest()
        if remote_file_hash and remote_file_hash == local_file_hash:
            print("File is already up to date. No need to download.")
        else:
            download_file(url, local_filename)
            shipping_costs = parse_file(local_filename)
            save(shipping_costs)
    else:
        download_file(url, local_filename)
        shipping_costs = parse_file(local_filename)
        save(shipping_costs)

if __name__ == '__main__':
    main()
