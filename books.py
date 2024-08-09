class Book:#リソースに対して操作を行うためのurlはエンドポイント　https://localhost:5000/books/{id} books
    def __init__(self, id, title, author):
        self.id = id #一意の識別子
        self.title = title
        self.author = author
        self.is_borrowed = False

books = [] #データ保管