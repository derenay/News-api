import requests


"""
https://ahrefs.com/blog/google-advanced-search-operators/

google search commands


    
"""



class CustomSearch:
    def __init__(self, query:str, date:str):
        self.url = "https://www.googleapis.com/customsearch/v1"
        self.api_key = "API_KEY"
        self.search_engine_id = "SEARCH_ENGINE_ID" # The Programmable Search Engine ID to use for this request.
        self.linkSite:str = None #Specifies that all search results should contain a link to a particular URL.
        self.lr:str = None # Restricts the search to documents written in a particular language (e.g., lr=lang_ja).
        self.hq:str = None #Appends the specified query terms to the query, as if they were combined with a logical AND operator.
        self.gl:str = None # The gl parameter value is a two-letter country code. The gl parameter boosts search results whose country of origin matches the parameter value. See the Country Codes page for a list of valid values.
        self.filter:str = None # Controls turning on or off the duplicate content filter. 0: Turns off duplicate content filter.  1: Turns on duplicate content filter.
        self.exactTerms:str = None # Identifies a phrase that all documents in the search results must contain.
        self.dateRestrict:str = date #Restricts results to URLs based on date. Supported values include: d[number]: requests results from the specified number of past days. w[number]: requests results from the specified number of past weeks. m[number]: requests results from the specified number of past months. y[number]: requests results from the specified number of past years.
        self.search_query:str = query
        
        self.params = {
            'q': self.search_query, 
            'key': self.api_key,     
            'cx': self.search_engine_id,  
            "dateRestrict": self.dateRestrict      
        }
                
        
    def search(self):

        response = requests.get(self.url, params=self.params)
        
        return response
    
    # belki sonradan dışardan ayarlanabilecek kısım
    def custom_params(self ,**kwargs):
        
        self.params = kwargs
    
    


if __name__=="__main__":
    
    query = ' "fenerbahçe" and "kadıköy"'
    date="d3"
 
    search = CustomSearch(query=query, date=date)
    response = search.search()

    if response.status_code == 200:
        search_results = response.json()
        items = search_results.get('items', [])
     
        for item in items:
            print(f"Başlık: {item['title']}")
            print(f"Açıklama: {item['snippet']}")
            print(f"Link: {item['link']}")
            print(f"Yayın Tarihi: {item.get('pagemap', {}).get('metatags', [{}])[0].get('article:published_time', 'Bilinmiyor')}")
            print("-" * 80)
    else:
        print(f"Hata: {response.status_code} - {response.text}")


    pass

    

    


