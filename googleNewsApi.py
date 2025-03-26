import datetime as dt
import hashlib
import json
import math
import os
import re
import pandas as pd
import requests

# Global değişkenler (toplam veri sayısı ve çekilen sayfa sayısını izlemek için)
_total_data_count = 0
_total_page_count = 0


def read_excel_data(excel_path: str = "websites_list.xlsx"):
    """
    Belirtilen Excel dosyasını okuyarak 'Website' sütunundaki verileri
    liste olarak döner.
    """
    data = pd.read_excel(excel_path)
    return data


def generate_dynamic_queries(search_key, search_dates, excel_path, max_length=660):
    """
    Excel dosyasındaki websiteleri, sorgunun toplam uzunluğu (örneğin 660 karakter)
    aşılmayacak şekilde dinamik olarak gruplar. Böylece sabit group_size yerine,
    query template'e sığacak kadar site eklenir.
    """
    # Excel'den siteleri oku
    data = read_excel_data(excel_path)
    websites = data["Website"].to_list()

    # Sorgunun sabit kısmı; site kısmı {} ile placeholder
    query_template = (
        f'{search_key} -inurl:topic -inurl:entertainment -intitle:news '
        f'-inurl:watch -inurl:tag {search_dates} ({{}})'
    )

    # Sorgunun sabit kısmının uzunluğu (site kısmı boşken)
    base_query_length = len(query_template.format(""))
    remaining_length = max_length - base_query_length

    queries = []
    temp_sites = []
    temp_length = 0

    # Her siteyi "site:xxx OR" şeklinde ekleyip toplam uzunluğu kontrol ediyoruz.
    for site in websites:
        site_query = f"site:{site} OR "
        site_length = len(site_query)

        # Eğer yeni site eklenince toplam uzunluk limiti aşılacaksa,
        # mevcut grup tamamlanmış demektir.
        if temp_length + site_length > remaining_length:
            # Son " OR " kısmını kaldırmak için [:-4] kullanıyoruz.
            final_sites = "".join(temp_sites)[:-4]
            final_query = query_template.format(final_sites)
            queries.append(final_query)
            # Yeni grup için resetle
            temp_sites = []
            temp_length = 0

        temp_sites.append(site_query)
        temp_length += site_length

    # Kalan siteler varsa, bunlarla son sorguyu oluştur
    if temp_sites:
        final_sites = "".join(temp_sites)[:-4]
        final_query = query_template.format(final_sites)
        queries.append(final_query)

    return queries


def send_request(query, API_KEY, CX_ID, start=1):
    """
    Google Custom Search API'ye GET isteği gönderir.
    """
    url = (
        f"https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}"
        f"&cx={CX_ID}&filter=1&start={start}"
    )
    print(f"Request URL: {url}")
    return requests.get(url)


def save_data(data, results, links, original_topic_name, topicID):
    """
    API'den gelen veriden her bir sonucun başlık, link ve snippet bilgisini
    alarak sonuçlara ekler.
    """
    global _total_data_count
    count = 0

    if "items" in data:
        for item in data["items"]:
            link = item.get("link")
            links.append(link)
            hashed_url = hashlib.sha256(link.encode("utf-8")).hexdigest()

            timestamp = int(dt.datetime.now().timestamp() * 1000)
            hashed_url = str(timestamp) + "_" + hashed_url
            results.append({
                "topicName": original_topic_name,
                "topicID": topicID,
                "title": item.get("title", None),
                "url": link,
                "description": item.get("snippet", None),
                "datePublished": item.get("pagemap", {}).get("metatags", [{}])[0].get("article:published_time", None),
                "source": item.get("displayLink", None),
                "author": item.get("article:author", None),
                "urlToImage": item.get("pagemap", {}).get("cse_thumbnail", [{}])[0].get("src", None),
                "content": item.get("pagemap", {}).get("metatags", [{}])[0].get("og:description", None),
                "file_name": hashed_url,
                "sensorType": "News Site",
                "mediaType": "Document",
                "sensorCategory": "OSS",
                "contentCreateTime": dt.datetime.now().isoformat(),
                "sensorTypeName": "Google API"
            })
            count += 1
        _total_data_count += count
    print(f"Toplam {count} sonuç işlendi bu sorguda.")
    return count


def create_json_path_and_save(original_topic_name, folder="results"):
    """
    Aranan konuya göre yeni JSON dosya yolu oluşturur ve boş bir JSON dosyası
    oluşturur.
    """
    if not os.path.exists(folder):
        os.makedirs(folder)

    
    
    safe_search_key = original_topic_name
  

    
    filename = f"{safe_search_key}.json"
    file_path = os.path.join(folder, filename)

    with open(file_path, "w", encoding="utf-8") as new_file:
        new_file.write("{}")
    print(f"Yeni JSON dosyası oluşturuldu: {filename}")
    return file_path


def save_json_file(search_key, original_topic_name, results, folder):
    """
    Sonuçları belirlenen dosya yoluna JSON formatında kaydeder.
    """
    file_path = create_json_path_and_save(original_topic_name, folder)
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(results, json_file, ensure_ascii=False, indent=4)
    print(f"Sonuçlar '{file_path}' dosyasına kaydedildi.")


def process_response(
    response, results, links, query, API_KEY, CX_ID,
                     original_topic_name, topicID, page_index_count):
    """
    İlk response'u işleyip kaydeder. Eğer toplam sonuç sayısı 10’dan
    büyükse, ek sayfa istekleri yapılır. Ek sayfalardan dönen sonuç sayısı
    5’ten azsa, istek durdurulur.
    """
    global _total_page_count
    data = response.json()
    total_results = int(data["searchInformation"]["totalResults"])

    results_per_page = 10
    total_pages = math.ceil(total_results / results_per_page)
    _total_page_count += 1  # İlk sayfa sayılıyor

    # İlk sayfa verisini kaydet
    save_data(data, results, links, original_topic_name, topicID)

    # Eğer toplam sonuç 10'dan fazla ise ek sayfa istekleri yap
    if total_results > 10:
        # Verilen mantığı koruyoruz
       
        start_indices = [start for start in range(11, min(total_results, int(page_index_count)), results_per_page)]
        # Eğer start_indices boşsa (örneğin total_results >= 11 olduğunda),
        # en azından ikinci sayfa için tek bir istek yapılmasını sağlıyoruz.
        if not start_indices:
            start_indices = [11]
        for start in start_indices:
            response = send_request(query, API_KEY, CX_ID, start=start)
            if response.status_code != 200:
                print(f"Başlangıç index {start} için hata oluştu: "
                      f"{response.status_code}")
                break

            data = response.json()
            articles = data.get("items", [])
            if not articles:
                print("No articles found.")
                break

            # Bu sayfanın verisini kaydet
            save_data(data, results, links, original_topic_name, topicID)
            _total_page_count += 1

            # Eğer bu sayfada dönen sonuç sayısı 5'ten azsa, ek istek yapılmaz
            if len(articles) < 5:
                break
    else:
        # Toplam sonuç 10 veya daha az ise, ilk sayfa kaydedildikten sonra başka istek yapılmaz.
        pass

    return total_results, total_pages



def main(search_key: str,
         original_topic_name: str,
         search_dates: str,
         topicId,
         excel_path: str,
         page_index_count:int= 21,
         folder: str = "folder",
         API_KEY: str = "AIzaSyBhC3wcdyK8ExV-77fnKv9Hbx8OLG4vUb8",
         CX_ID: str = "221a514978cf94520") -> None:
    """
    Tüm süreci yönetir: dinamik sorguları oluşturur, API isteklerini yapar,
    sonuçları kaydeder.
    """
    global _total_data_count, _total_page_count
    _total_data_count = 0
    _total_page_count = 0

    queries = generate_dynamic_queries(search_key, search_dates, excel_path)

    results = []
    links = []

    for query in queries:
        response = send_request(query, API_KEY, CX_ID, start=1)
        if response.status_code == 200:
            process_response(response, results, links, query, API_KEY, CX_ID,
                             original_topic_name, topicId, page_index_count)
        else:
            print("API isteğinde hata oluştu:", response.status_code)

    save_json_file(search_key, original_topic_name, results, folder)

    print("\nÖzet:")
    print(f"Toplam çekilen veri sayısı: {_total_data_count}")
    print(f"Çekilen toplam sayfa sayısı: {_total_page_count}")


if __name__ == "__main__":
    main(
        search_key='("Labour Violation" OR "Workers Rights" OR "Workers Right" OR "Decent Work" OR "Labor Violation" OR "Waight" OR "Workers Conditions")',
        original_topic_name="Labour Violation",
        search_dates="after:2025-03-23 before:2025-03-25",
        topicId="123",
        excel_path="websites_list.xlsx",
        page_index_count=21,
        folder="req"
    )
