#エントリーポイント

from flask import Flask, request, json, jsonify
from books import Book, books

app = Flask(__name__) #Flaskのインスタンスを生成 appに代入 nameは現在のモジュール名

@app.route('/books', methods=['POST']) #デコレーター　URLと関数を結びつける /はルート urlのルートにアクセスしたら次の関数を実行
def add_book():
    data = request.get_json() #リクエストのjsonを取得

    book_id = len(books) + 1

    new_book = Book(id=book_id, title=data.get('title'), author = data.get('author'))
    books.append(new_book)

    response_data = {
        "message":"本の登録に成功しました。", 
        "book":{"id":new_book.id,
                "title":new_book.title, 
                "author":new_book.author
        }
    }
    response_json = json.dumps(response_data, ensure_ascii=False) #json形式に変換
    return response_json, 201 #201はリソースが作成されたことを示すステータスコード

@app.route('/books/<int:book_id>', methods=['PUT']) #<int:book_id>は変数を受け取る　int型に変換
def update_book(book_id):
    data = request.get_json()

    book_to_update = next((book for book in books if book.id == book_id), None)

    if not book_to_update:
        #return jsonify({"message":"本が見つかりません"}), 404
        return json.dumps({"message":"本が見つかりません"},ensure_ascii=False),404
    
    if 'title' in data:
        book_to_update.title = data['title']

    if 'author' in data:
        book_to_update.author = data['author']

    return json.dumps({"message":"本の更新に成功しました",
                    "book":{"id":book_to_update.id,
                            "title":book_to_update.title,
                            "author":book_to_update.author}},ensure_ascii=False),200

@app.route('/books/<int:book_id>', methods=['PATCH'])
def update_borrowing_status(book_id):
    book = next((b for b in books if b.id == book_id), None)

    if not book:
        return json.dumps({"message":"本が見つかりません"},ensure_ascii=False),404
    
    data = request.get_json()

    if 'action' not in data:
        return json.dumps({"message":"actionが指定されていません"},ensure_ascii=False),400
    
    if data['action'] == 'borrow':
        if book.is_borrowed:
            return json.dumps({"message":"本はすでに貸し出されています"},ensure_ascii=False),400
        book.is_borrowed = True
        return json.dumps({"message":"本の貸し出しに成功しました",
                            "book":{"id":book.id,
                                    "title":book.title,
                                    "author":book.author,
                                    "is_borrowed":book.is_borrowed}},ensure_ascii=False),200
    
    elif data['action'] == 'return':
        if not book.is_borrowed:
            return json.dumps({"message":"本は貸し出されていません"},ensure_ascii=False),400
        book.is_borrowed = False
        return json.dumps({"message":"本の返却に成功しました",
                        "book":{"id":book.id,
                                "title":book.title,
                                "author":book.author,
                                "is_borrowed":book.is_borrowed}},ensure_ascii=False),200
    
    else:
        return json.dumps({"message":"actionが不正です"},ensure_ascii=False),400
    
@app.route('books', methods=['GET'])

def get_books():
    title_query = request.args.get('title', None, type=str)
    author_query = request.args.get('author', None, type=str)
    fields = request.args.get('fields', None, type=str)

    filtered_books = books
    if title_query:
        filtered_books = [b for b in filtered_books if title_query.lower() in b.title_query.lower()]
    if author_query:
        filtered_books = [b for b in filtered_books if author_query.lower() in b.author_query.lower()]
    
    if not filtered_books:
        return json.dumps({"message":"本が見つかりません"},ensure_ascii=False),404
    
    response_books = []
    for book in filtered_books:
        status_msg = "貸し出し中" if book.is_borrowed else "貸し出し可能"
        book_data = {
            "id":book.id,
            "title":book.title, 
            "author":book.author, 
            "status":status_msg
        }

        if fields:
            fields_list = fields.split(',')
            book_data = {key: book_data[key] for key in fields_list if key in book_data}

        response_books.append(book_data)
    
    response = {"books":response_books}
    if len(response_books) > 1:
        response["count"] = len(response_books)

    return json.dumps(response, ensure_ascii=False),200
    
if __name__ == '__main__':
    app.run(debug = True) #デバッグモードで実行 #コードに変更があった場合自動で再起動　セキュリティ的にはよくない　本番環境ではFalseにする

