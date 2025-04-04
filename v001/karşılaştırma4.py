# -*- coding: utf-8 -*-
import json
import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import os

# --- NLTK Veri Kontrolü ve İndirme ---
# İlk çalıştırmada hata alırsanız aşağıdaki satırların yorumunu kaldırıp çalıştırın:
# try:
#     nltk.data.find('tokenizers/punkt')
# except nltk.downloader.DownloadError:
#     print("NLTK 'punkt' verisi indiriliyor...")
#     nltk.download('punkt', quiet=True)
# try:
#     nltk.data.find('corpora/stopwords')
# except nltk.downloader.DownloadError:
#     print("NLTK 'stopwords' verisi indiriliyor...")
#     nltk.download('stopwords', quiet=True)
# --- ---

# Ön işleme ayarları
stop_words = set(stopwords.words('english'))
ps = PorterStemmer()

def preprocess(text):
    """Metni temizler, tokenleştirir, stop wordleri çıkarır ve köklerini alır."""
    if not text or not isinstance(text, str):
        return ""
    # Küçük harfe çevirme (Büyük/küçük harf sorununu çözer)
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    tokens = word_tokenize(text)
    tokens = [w for w in tokens if w not in stop_words]
    tokens = [ps.stem(w) for w in tokens]
    return ' '.join(tokens)

def read_json(file_path):
    """JSON dosyasını okur ve içeriğini döndürür."""
    if not os.path.exists(file_path):
        print(f"Hata: Dosya bulunamadı - {file_path}")
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, list):
                # Eğer sadece tek bir nesne ise, onu liste içine al
                if isinstance(data, dict):
                     print(f"Uyarı: JSON dosyası ({file_path}) tek bir nesne içeriyor, liste içine alınıyor.")
                     return [data]
                else:
                    print(f"Hata: JSON dosyasının içeriği bir liste veya nesne değil - {file_path}")
                    return None
            return data
    except json.JSONDecodeError as e:
        print(f"JSON okuma hatası: {file_path} - {str(e)}")
        return None
    except Exception as e:
        print(f"Genel dosya hatası: {file_path} - {str(e)}")
        return None

def calculate_internal_duplicates(data, text_fields, threshold=0.4):
    """Veri kümesi içindeki tekrar eden öğeleri TF-IDF ve kosinüs benzerliği ile bulur."""
    if not data or len(data) < 2:
        return [], 0.0

    texts = [' '.join(str(item.get(f, '') or '') for f in text_fields) for item in data]
    processed = [preprocess(t) for t in texts]

    valid_indices = [i for i, t in enumerate(processed) if t]
    if len(valid_indices) < 2:
        return [], 0.0
    
    filtered_processed = [processed[i] for i in valid_indices]
    
    try:
        vectorizer = TfidfVectorizer().fit(filtered_processed)
        vectors = vectorizer.transform(filtered_processed)
    except ValueError as e:
         print(f"TF-IDF Vektörleyici Hatası (İçsel Tekrar): {e}.")
         return [], 0.0
         
    sim_matrix = cosine_similarity(vectors)

    duplicates_indices_in_filtered = set()
    original_duplicate_indices = set() # Orijinal indexleri saklamak için
    for i in range(len(sim_matrix)):
        for j in range(i + 1, len(sim_matrix)):
            if sim_matrix[i, j] > threshold:
                original_idx_j = valid_indices[j]
                original_duplicate_indices.add(original_idx_j)

    duplicate_rate = (len(original_duplicate_indices) / len(data)) * 100 if data else 0.0
    return list(original_duplicate_indices), duplicate_rate

def calculate_keyword_relevance(data, keywords, text_fields):
    """
    Verilen anahtar kelimelerin her birinin veri kümesindeki metin alanlarında
    ne sıklıkla geçtiğini sayar (büyük/küçük harf duyarsız) ve toplam alakadar
    öğe sayısını döndürür.

    Döndürülenler:
        tuple: (relevance_counts (dict), total_relevant_items (int))
               relevance_counts: {keyword_lower: count}
               total_relevant_items: Anahtar kelimelerden en az birini içeren öğe sayısı.
    """
    if not data:
        return {kw.lower(): 0 for kw in keywords} if keywords else {}, 0

    # Anahtar kelimeleri bir kereliğine küçük harfe çevirip set yapalım (hızlı kontrol için)
    lower_keywords = {kw.lower() for kw in keywords if kw} # Boş keywordleri atla
    if not lower_keywords: # Eğer geçerli keyword yoksa
         return {}, 0

    relevance_counts = {kw: 0 for kw in lower_keywords}
    total_relevant_items = 0

    for item in data:
        # Metinleri birleştirirken None/boş değer kontrolü ve küçük harfe çevirme
        text = ' '.join(str(item.get(f, '') or '').lower() for f in text_fields)
        if not text:
            continue

        item_is_relevant = False
        matched_keywords_in_item = set() # Bir öğede aynı keyword'ü tekrar saymamak için

        for kw_lower in lower_keywords:
             # Basit alt dize kontrolü yapıyoruz
             if kw_lower in text:
                 item_is_relevant = True # Bu öğe en az bir keyword içeriyor
                 if kw_lower not in matched_keywords_in_item:
                     relevance_counts[kw_lower] += 1
                     matched_keywords_in_item.add(kw_lower)

        if item_is_relevant:
            total_relevant_items += 1

    # Orijinal keyword listesindeki sıraya ve büyük/küçük harfe göre sonucu formatla (isteğe bağlı)
    # final_counts = {orig_kw: relevance_counts.get(orig_kw.lower(), 0) for orig_kw in keywords if orig_kw}
    # return final_counts, total_relevant_items

    return relevance_counts, total_relevant_items # Küçük harfli anahtarlarla döndür


def find_cross_similarity(google_data, news_data, google_text_fields, news_text_fields, threshold=0.20):
    """
    İki farklı veri kümesi (Google ve News API) arasındaki benzer öğeleri bulur.
    Her Google öğesi için en iyi eşleşen News öğesini (eğer eşik üzerindeyse) bulur.
    """
    g_texts = [preprocess(' '.join(str(item.get(f, '') or '') for f in google_text_fields)) for item in google_data]
    n_texts = [preprocess(' '.join(str(item.get(f, '') or '') for f in news_text_fields)) for item in news_data]

    valid_g_indices = [i for i, t in enumerate(g_texts) if t]
    valid_n_indices = [i for i, t in enumerate(n_texts) if t]

    if not valid_g_indices or not valid_n_indices:
        print("Uyarı: Çapraz benzerlik için yeterli geçerli metin bulunamadı.")
        return []

    filtered_g_texts = [g_texts[i] for i in valid_g_indices]
    filtered_n_texts = [n_texts[i] for i in valid_n_indices]

    try:
        vectorizer = TfidfVectorizer().fit(filtered_g_texts + filtered_n_texts)
        g_vectors = vectorizer.transform(filtered_g_texts)
        n_vectors = vectorizer.transform(filtered_n_texts)
    except ValueError as e:
        print(f"TF-IDF Vektörleyici Hatası (Çapraz Benzerlik): {e}.")
        return []
        
    sim_matrix = cosine_similarity(g_vectors, n_vectors)

    matches = []
    used_news_indices_in_filtered = set()

    for i in range(sim_matrix.shape[0]):
        best_score = -1
        best_n_idx_in_filtered = -1

        for j in range(sim_matrix.shape[1]):
            if j not in used_news_indices_in_filtered and sim_matrix[i, j] > best_score:
                best_score = sim_matrix[i, j]
                best_n_idx_in_filtered = j

        if best_score >= threshold and best_n_idx_in_filtered != -1:
            original_g_idx = valid_g_indices[i]
            original_n_idx = valid_n_indices[best_n_idx_in_filtered]

            matches.append({
                'google_title': google_data[original_g_idx].get('title'),
                'news_title': news_data[original_n_idx].get('title'),
                'similarity': float(best_score),
                'google_url': google_data[original_g_idx].get('url'),
                'news_url': news_data[original_n_idx].get('link'),
                'google_index': original_g_idx,
                'news_index': original_n_idx
            })
            used_news_indices_in_filtered.add(best_n_idx_in_filtered)
            
    matches.sort(key=lambda x: x['similarity'], reverse=True)
    return matches

def analyze_datasets(google_file, news_file, keywords_to_analyze, output_file,
                     google_fields=['title', 'description'],
                     news_fields=['title', 'snippet'],
                     internal_dup_threshold=0.4,
                     cross_sim_threshold=0.25):
    """Ana analiz fonksiyonu: Verileri okur, analizleri yapar ve sonuçları JSON olarak kaydeder."""

    print("Analiz başlıyor...")
    google_data = read_json(google_file)
    news_data = read_json(news_file)

    if google_data is None or news_data is None:
        print("Veri dosyaları okunamadığı için analiz durduruldu.")
        return None
        
    # Başlangıç öğe sayıları
    google_total_items = len(google_data)
    news_total_items = len(news_data)
    print(f"Google verisi: {google_total_items} öğe, News API verisi: {news_total_items} öğe.")
    
    if not google_data and not news_data:
        print("Her iki veri seti de boş. Analiz yapılamıyor.")
        return None # İki set de boşsa devam etmenin anlamı yok

    # 1. İçsel tekrar oranı hesaplama
    print("İçsel tekrarlar hesaplanıyor...")
    google_dup_indices, google_dup_rate = calculate_internal_duplicates(
        google_data, google_fields, threshold=internal_dup_threshold
    ) if google_data else ([], 0.0)
    news_dup_indices, news_dup_rate = calculate_internal_duplicates(
        news_data, news_fields, threshold=internal_dup_threshold
    ) if news_data else ([], 0.0)

    unique_google = [item for idx, item in enumerate(google_data)
                     if idx not in google_dup_indices] if google_data else []
    unique_news = [item for idx, item in enumerate(news_data)
                   if idx not in news_dup_indices] if news_data else []
    print(f"Tekrarlar sonrası Google: {len(unique_google)} öğe, News API: {len(unique_news)} öğe.")

    # 2. Anahtar kelime analizi ve Alaka Düzeyi (Tüm veri üzerinde)
    print(f"Anahtar kelime analizi ve alaka düzeyi hesaplanıyor: {keywords_to_analyze}")
    google_keyword_counts, google_relevant_items = calculate_keyword_relevance(
        google_data, keywords_to_analyze, google_fields
    ) if google_data else ({}, 0)
    news_keyword_counts, news_relevant_items = calculate_keyword_relevance(
        news_data, keywords_to_analyze, news_fields
    ) if news_data else ({}, 0)

    # Alakasız öğe sayıları ve oranları
    google_irrelevant_items = google_total_items - google_relevant_items
    google_irrelevancy_rate = (google_irrelevant_items / google_total_items * 100) if google_total_items > 0 else 0.0
    
    news_irrelevant_items = news_total_items - news_relevant_items
    news_irrelevancy_rate = (news_irrelevant_items / news_total_items * 100) if news_total_items > 0 else 0.0

    print(f"Google - Alakalı: {google_relevant_items}, Alakasız: {google_irrelevant_items} (%{google_irrelevancy_rate:.2f})")
    print(f"News API - Alakalı: {news_relevant_items}, Alakasız: {news_irrelevant_items} (%{news_irrelevancy_rate:.2f})")

    # 3. Çapraz Benzerlik analizi (Tekrarlamayan veri üzerinde)
    print("Çapraz benzerlik analizi yapılıyor...")
    cross_matches = find_cross_similarity(
        unique_google, unique_news,
        google_fields, news_fields,
        threshold=cross_sim_threshold
    ) if unique_google and unique_news else [] # Sadece her iki liste de boş değilse çalıştır
    print(f"{len(cross_matches)} adet çapraz eşleşme bulundu.")

    # Sonuçları yapılandırma
    result = {
        'analysis_parameters': {
            'google_file': google_file,
            'news_file': news_file,
            'keywords_analyzed': keywords_to_analyze,
            'google_text_fields': google_fields,
            'news_text_fields': news_fields,
            'internal_duplicate_threshold': internal_dup_threshold,
            'cross_similarity_threshold': cross_sim_threshold
        },
        'statistics': {
            'google': {
                'total_items': google_total_items,
                'duplicate_items': len(google_dup_indices),
                'duplicate_rate_percent': round(google_dup_rate, 2),
                'unique_items': len(unique_google),
                'relevant_items': google_relevant_items, # Yeni eklendi
                'irrelevant_items': google_irrelevant_items, # Yeni eklendi
                'irrelevancy_rate_percent': round(google_irrelevancy_rate, 2), # Yeni eklendi
                'keyword_relevance_counts': google_keyword_counts # İsim daha açıklayıcı oldu
            },
            'news_api': {
                'total_items': news_total_items,
                'duplicate_items': len(news_dup_indices),
                'duplicate_rate_percent': round(news_dup_rate, 2),
                'unique_items': len(unique_news),
                'relevant_items': news_relevant_items, # Yeni eklendi
                'irrelevant_items': news_irrelevant_items, # Yeni eklendi
                'irrelevancy_rate_percent': round(news_irrelevancy_rate, 2), # Yeni eklendi
                'keyword_relevance_counts': news_keyword_counts # İsim daha açıklayıcı oldu
            }
        },
        'cross_matches': cross_matches
    }

    # Sonuçları JSON dosyasına yazma
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        print(f"Analiz tamamlandı. Sonuçlar '{output_file}' dosyasına kaydedildi.")
    except Exception as e:
        print(f"Sonuçları dosyaya yazarken hata oluştu: {output_file} - {str(e)}")

    return result

# --- Kullanım Örneği ---
if __name__ == "__main__":
    google_json_file = "req/Child abuse.json"
    news_json_file = "exact-child_slavery.json"
    keywords = ["child abuse", "abuse", "child"] # Daha fazla keyword ekledim
    output_json_file = "full_analysis_v3.json" # Yeni versiyon için farklı dosya adı

    analysis_results = analyze_datasets(
        google_file=google_json_file,
        news_file=news_json_file,
        keywords_to_analyze=keywords,
        output_file=output_json_file
    )

    # Örnek Çıktı Özeti (İsteğe Bağlı)
    # if analysis_results:
    #    print("\n--- Analiz Özeti (İstatistikler) ---")
    #    print(json.dumps(analysis_results['statistics'], indent=2))