import requests

def search_books(query, max_results=10):
    """
    Google Books APIを使用して書籍を検索する
    """
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults={max_results}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if 'items' not in data:
            return []
        
        books = []
        for item in data['items']:
            volume_info = item.get('volumeInfo', {})
            
            # サムネイル画像のURLを取得
            thumbnail = None
            if 'imageLinks' in volume_info and 'thumbnail' in volume_info['imageLinks']:
                thumbnail = volume_info['imageLinks']['thumbnail']
            
            # 必要な情報を抽出
            book = {
                'id': item.get('id'),
                'title': volume_info.get('title', '不明'),
                'authors': volume_info.get('authors', ['不明']),
                'publisher': volume_info.get('publisher', ''),
                'publishedDate': volume_info.get('publishedDate', ''),
                'description': volume_info.get('description', ''),
                'pageCount': volume_info.get('pageCount', 0),
                'categories': volume_info.get('categories', []),
                'thumbnail': thumbnail,
                'language': volume_info.get('language', ''),
                'industryIdentifiers': volume_info.get('industryIdentifiers', [])
            }
            
            books.append(book)
        
        return books
    
    except Exception as e:
        print(f"Error searching books: {e}")
        return []

def get_book_by_id(book_id):
    """
    Google Books APIを使用して特定のIDの書籍情報を取得する
    """
    url = f"https://www.googleapis.com/books/v1/volumes/{book_id}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if 'volumeInfo' not in data:
            return None
        
        return data['volumeInfo']
    
    except Exception as e:
        print(f"Error getting book: {e}")
        return None 