import requests
import math
import json
import os
import re
import time

# Google API bilgileri
 #API_KEY = "AIzaSyBGqcE-0a1smoF96XidQP8piPbvSUmL4p4"
API_KEY = "AIzaSyBhC3wcdyK8ExV-77fnKv9Hbx8OLG4vUb8"
CX_ID = "b0b54261ce0424f8e"

# Arama sorgusu 
query = '(intext:"child abuse" OR "child abuse") after:2024-07-01 before:2024-07-20'

# Sonuçları saklayacağımız liste
results = []
links = []

# API isteği gönderme fonksiyonu
def send_request(start=1):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={CX_ID}&filter=1&start={start}"
    print(f"url:{url}")
    
    return requests.get(url)

# Gelen veriyi işleyip gerekli bilgileri çıkartma
def get_data(response, results):
    data = response.json()

    # Toplam sonuç sayısını al
    total_results = int(data["searchInformation"]["totalResults"])
    print(f"Toplam Sonuç Sayısı: {total_results}")

    # Sayfa sayısını hesapla (her sayfa 10 sonuç içeriyor)
    results_per_page = 10
    total_pages = math.ceil(total_results / results_per_page)
    print(f"Toplam Sayfa Sayısı: {total_pages}")

    # Sayfaları çekmek için start parametrelerini oluştur
    start_indices = [start for start in range(11, total_results, results_per_page)]

    if total_pages > 1:
        for i in start_indices:
       
            if response.status_code == 200:
                save_data(response.json(), results) # gelen response ve response listesi save_dataya yönlendirilir ve dosyaya yazım başlar yada devam ederS
                print("burdaki çalıştı")
            else:
                print(f"Error occurred while fetching data for start index {i}: {response.status_code}")
            
            if i >= 31: # her bir sayfayı gezerken belirlediğiniz yerde durmasını sağlar
                break
            response = send_request(start=i) 
            print("Response yollandı")
           
    else:
        print("selam")
        save_data(data, results)
    

    with open(f"{create_path()}", "w", encoding="utf-8") as json_file:
        json.dump(results, json_file, ensure_ascii=False, indent=4)

    print("Sonuçlar 'results.json' dosyasına kaydedildi.")




def create_path():
    folder_path = 'results'
    # Dosya isimleri için regex desenini tanımlayın (örneğin: results1.json, results2.json, vb.)
    pattern = r'results(\d+)\.json'
    files = os.listdir(folder_path)

    numbers = []
    for file in files:
        match = re.match(pattern, file)
        if match:
            numbers.append(int(match.group(1)))

    if numbers:
        next_number = max(numbers) + 1
    else:
        next_number = 1  

    new_filename = f'results{next_number}.json'
    new_file_path = os.path.join(folder_path, new_filename)
    
    with open(new_file_path, 'w') as new_file:
        new_file.write('{}')  
        
    print(f"Yeni dosya oluşturuldu: {new_filename}")
    return new_file_path


# Verileri kaydetme
def save_data(data, results):
    print()
    print(data)
    print()
    print("save_data çalıştı")
    number = 0
    if "items" in data:
        print()
        print(data["items"])
        print()
        for item in data["items"]:
            link = item.get("link")
            links.append(link)
            results.append({
                "title": item.get("title"),
                "link": link,
                "snippet": item.get("snippet")
            })
            number+=1
        print(f"number counts{number}")
    print(results)
            

# Ana fonksiyon
def main():
    response = send_request(start=1)
    if response.status_code == 200:
        get_data(response, results)
    else:
        print("API isteğinde hata oluştu:", response.status_code)

if __name__ == "__main__":
    main()
