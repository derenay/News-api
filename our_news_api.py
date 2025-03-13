import requests
import math
import json
import os
import re
import time

# Google API bilgileri
#API_KEY = "AIzaSyBGqcE-0a1smoF96XidQP8piPbvSUmL4p4"    AIzaSyBhC3wcdyK8ExV-77fnKv9Hbx8OLG4vUb8
API_KEY = "AIzaSyBGqcE-0a1smoF96XidQP8piPbvSUmL4p4"
CX_ID = "221a514978cf94520"   #b0b54261ce0424f8e  221a514978cf94520
 
search_key = "andrew tate" #after:2024-08-01 before:2024-08-28
search_dates = "after:2024-08-01 before:2024-08-28"

"""google query 2000 den fazla karekter almıyor dikkatli kullan alanını yada yeni query oluştur"""

query_one = 'site:cnn.com OR site:theguardian.com OR site:nytimes.com OR site:reuters.com OR site:aljazeera.com OR site:euronews.com OR site:bbc.co.uk OR site:abcnews.go.com OR site:forbes.com OR site:washingtonpost.com OR site:thehindu.com OR site:theatlantic.com OR site:businessinsider.com OR site:ft.com OR site:wsj.com OR site:usnews.com OR site:telegraph.co.uk OR site:theverge.com OR site:npr.org OR site:foxnews.com OR site:globalnews.ca OR site:latimes.com OR site:independent.co.uk OR site:sky.com OR site:cnn.co.uk OR site:nydailynews.com OR site:lemonde.fr OR site:lesechos.fr OR site:spiegel.de OR site:zeit.de OR site:derstandard.at OR site:rt.com OR site:southchinamorningpost.com OR site:cbc.ca OR site:scmp.com OR site:newsweek.com OR site:thetimes.co.uk OR site:independent.ie OR site:reuters.co.uk OR site:bloomberg.com OR site:elpais.com OR site:theguardian.com.au OR site:thehill.com OR site:democracynow.org OR site:voanews.com OR site:sydneymorningherald.com.au OR site:news.com.au OR site:express.co.uk OR site:chinadaily.com.cn OR site:arabnews.com OR site:al-monitor.com OR site:focustaiwan.tw OR site:taipeitimes.com OR site:taiwannews.com.tw OR site:walkfree.org OR site:maritime-executive.com OR site:wnd.com'
query_two = 'site:egypttoday.com OR site:thearabweekly.com OR site:middleeasteye.net OR site:thenationalnews.com OR site:iranintl.com/en OR site:haaretz.com OR site:english.alarabiya.net OR site:almasdarnews.com OR site:asiatimes.com OR site:asianews.network OR site:wionews.com OR site:asahi.com/ajw OR site:edition.cnn.com/world/asia OR site:tass.com OR site:meduza.io/en OR site:deadspin.com OR site:frontpagedetectives.com OR site:thehollywoodgossip.com OR site:nypost.com OR site:thestar.com.my OR site:tmz.com OR site:thejakartapost.com OR site:koreaherald.com OR site:japantoday.com OR site:straitstimes.com/global OR site:manilatimes.net OR site:indiatoday.in OR site:themoscowtimes.com OR site:sputnikglobe.com OR site:turkmenistan.gov.tm/tk OR site:inform.kz OR site:theeastafrican.co.ke OR site:africanews.com OR site:thelocal.fr OR site:thelocal.de OR site:thelocal.es OR site:thelocal.it OR site:dutchnews.nl OR site:sweden.se OR site:thelocal.se OR site:ekathimerini.com OR site:greekreporter.com OR site:inquirer.net OR site:thejakartapost.com'
query_three = 'site:bangkokpost.com OR site:koreaherald.com OR site:japantimes.co.jp OR site:smh.com.au OR site:nzherald.co.nz OR site:bbc.com/news OR site:alquds.com/en OR site:alquds.com OR site:alquds.com/ar OR site:ashams.com OR site:english.aawsat.com OR site:ahram.org.eg OR site:english.ahram.org.eg OR site:jadaliyya.com OR site:alarabiya.net OR site:jordantimes.com OR site:jpost.com OR site:haaretz.com/middle-east-news* OR site:bbc.com/news/world/middle_east* OR site:reuters.com/world/middle-east/ OR site:middleeastmonitor.com OR site:aljazeera.com/middle-east/ OR site:usatoday.com OR site:yahoo.com OR site:bostonglobe.com OR site:usmagazine.com OR site:radaronline.com OR site:mibtraderumors.com OR site:nbcnews.com OR site:journals.plos.org OR site:rawstory.com OR site:psychologytoday.com OR site:eff.org OR site:eonline.com OR site:miamiherald.com OR site:people.com OR site:wired.com OR site:boredpanda.com OR site:abs-cbn.com OR site:rappler.com OR site:pna.gov.ph OR site:kathmandupost.com OR site:nepalnews.com OR site:timesofisrael.com OR site:jewishinsider.com'
query_four = 'site:theblaze.com OR site:roanoke.com OR site:rnz.co.nz OR site:hawaiinewsnnow.com OR site:healthychildren.org OR site:huffpost.com OR site:6abc.com OR site:9news.com.au OR site:fbi.gov OR site:westmidlands.police.uk OR site:pbs.org OR site:thejournal.ie OR site:tagesspiegel.de OR site:medianama.com OR site:naturalnews.com OR site:reason.com OR site:theroot.com OR site:thehillstimes.in OR site:timesofindia.indiatimes.com OR site:euractiv.com OR site:aajtak.in OR site:wonkette.com OR site:breitbart.com OR site:cbsnews.com OR site:hurriyetdailynews.com OR site:spectrumlocalnews.com OR site:kinglawoffices.com OR site:hopeandhomes.org OR site:advocate.com OR site:news24.com OR site:abc.net.au OR site:appleinsider.com OR site:readwrite.com OR site:guardian.com OR site:ilo.org OR site:go.kompas.com OR site:antaranews.com OR site:vaticannews.va OR site:hopeforjustice.org OR site:antislavery.org OR site:stopchildlabor.org OR site:akipress.com OR site:syriadirect.org OR site:enabbaladi.net OR site:afp.com/en OR site:pakistantoday.com.pk OR site:thenews.com.pk OR site:mothership.sg OR site:theindependent.sg OR site:todayonline.com OR site:channelnewsasia.com OR site:vietnamplus.vn OR site:vietnamnews.vn OR site:jagran.com OR site:cgtn.com'

queries = [
    f'"{search_key}" OR intitle:"{search_key}" OR {search_key} {search_dates} {query_one}',
    f'"{search_key}" OR intitle:"{search_key}" OR {search_key} {search_dates} {query_two}',
    f'"{search_key}" OR intitle:"{search_key}" OR {search_key} {search_dates} {query_three}',
    f'"{search_key}" OR intitle:"{search_key}" OR {search_key} {search_dates} {query_four}'
]


d = 0

# Sonuçları saklayacağımız liste
results = []
links = []


# API isteği gönderme fonksiyonu
def send_request(query, start=1):
    """
    Sends a GET request to the Google Custom Search API with the specified query and starting index.

    This function constructs a URL with the provided search query and start index, appends the API key and 
    Custom Search Engine ID, and sends a GET request to fetch the search results. The results are returned 
    as a response object.

    Args:
        query (str): The search query to send to the Google Custom Search API.
        start (int, optional): The starting index for the search results (default is 1). 
                               It determines which result page to fetch.

    Returns:
        Response: A response object containing the search results from the Google Custom Search API.

    """
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={CX_ID}&filter=1&start={start}"
    print(f"url:{url}")
    
    return requests.get(url)

# Gelen veriyi işleyip gerekli bilgileri çıkartma
def get_data(response, results, query):
    """
    Fetches search results data from a response, processes it, and saves the data to a results list.

    This function retrieves the total number of search results and calculates the number of pages required 
    to fetch all results, considering that each page contains 10 results. It then fetches additional results 
    by making further requests (if there are multiple pages) and processes each page of results. The data 
    is saved using the `save_data` function.

    The function will stop fetching additional pages if the total results exceed a certain threshold (e.g., 41 results).

    Args:
        response (Response): The initial response containing search results in JSON format. 
                              It should contain 'searchInformation' and 'items' keys.
        results (list): A list to store the processed search results. Each result is a dictionary containing 
                        'title', 'link', and 'snippet' information.
        query (str): The search query used for making subsequent requests when fetching additional pages of results.

    Returns:
        None: This function does not return a value. It processes the data and modifies the `results` list in place.
    """
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
            data = response.json()

            # Toplam sonuç sayısını al
            total_results = int(data["searchInformation"]["totalResults"])
            print(f"Toplam Sonuç Sayısı: {total_results}")

            # Sayfa sayısını hesapla (her sayfa 10 sonuç içeriyor)
            results_per_page = 10
            total_pages = math.ceil(total_results / results_per_page)
            print(f"Toplam Sayfa Sayısı: {total_pages}")
            if response.status_code == 200:
                save_data(response.json(), results) # gelen response ve response listesi save_dataya yönlendirilir ve dosyaya yazım başlar yada devam ederS
                print("burdaki çalıştı")
            else:
                print(f"Error occurred while fetching data for start index {i}: {response.status_code}")
            
            if i >= 41: # her bir sayfayı gezerken belirlediğiniz yerde durmasını sağlar
                break
            if total_results > 2:
                response = send_request(query ,start=i) 
                print("Response yollandı")
           
    else:
        print("selam")
        save_data(data, results)

    
def save_json_file():
    """
    Saves the collected results to a newly created JSON file.

    This function calls the `create_path` function to generate a new JSON file path. 
    It then writes the `results` data to this file, ensuring the content is properly formatted 
    with indentation for readability. The file is saved with UTF-8 encoding, and non-ASCII characters 
    are preserved.

    The results are saved in a structured JSON format with an indentation of 4 spaces.

    Returns:
        None: This function does not return any value. It writes data to a file.
    """
    file_path = create_path()
    with open(f"{file_path}", "w", encoding="utf-8") as json_file:
        json.dump(results, json_file, ensure_ascii=False, indent=4)

    print(f"Sonuçlar '{file_path}' dosyasına kaydedildi.")


def create_path():
    """
    Creates a new JSON file with an incremented filename based on existing files in the 'results' folder.

    This function checks for existing JSON files in the 'results' directory, identifies the highest number
    used in their filenames (e.g., 'results1.json', 'results2.json', etc.), and creates a new file with 
    the next sequential number (e.g., 'results3.json'). If no such files exist, it creates the first file 
    ('results1.json').

    The newly created file is initialized with an empty JSON object.

    Returns:
        str: The file path of the newly created JSON file.
    """
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
    """
    Saves relevant data from the input into a results list.

    This function processes the given data (which is expected to contain 
    items with 'title', 'link', and 'snippet' fields), and appends 
    each item's relevant information to the results list.

    Args:
        data (dict): A dictionary containing data to be processed. (This is comming from request response)
                     It should have an 'items' key, which is a list of items
                     where each item contains 'title', 'link', and 'snippet' keys.
        results (list): A list where the processed results will be appended.
                        Each result is a dictionary with 'title', 'link', and 'snippet' keys.

    Returns:
        None: This function does not return any value. It modifies the results list in place.
    """
    print()
    print(data)
    print()
    print("save_data çalıştı")
    number = 0
    global d
    if "items" in data:
        for item in data["items"]:
            link = item.get("link")
            links.append(link)
            results.append({
                "title": item.get("title"),
                "link": link,
                "snippet": item.get("snippet")
            })
            number+=1
        d +=number
        print(d)
    print(f"number counts{number}")

    

def take_query():
    
    
    
    pass



def main():
    """
    Main function to send search requests for multiple queries and process the results.

    This function iterates through a list of queries, sends a request for each query to the Google Custom 
    Search API, and processes the response. If the request is successful (status code 200), it passes the 
    response and query to the `get_data` function to fetch and store the results. After processing all queries, 
    it saves the results to a JSON file using the `save_json_file` function.

    Returns:
        None: This function does not return any value. It processes the search queries and saves the results.
    """
    for query in queries:
        response = send_request(query, start=1)
        if response.status_code == 200:
            get_data(response, results, query)
        else:
            print("API isteğinde hata oluştu:", response.status_code)
            
    save_json_file()

if __name__ == "__main__":
    main()
