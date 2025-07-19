

https://books.toscrape.com/

project_book_scrapping/
├── data/
│   └── books.csv           # <-- O arquivo gerado pelo seu script de scraping
├── scripts/
│   └── scrape_books.py     # <-- Seu código de scraping (o que você me mostrou)
├── api/
│   └── app.py              # <-- Sua aplicação Flask (a API)
├── .gitignore              # Arquivo para o Git ignorar pastas como 'venv', '__pycache__', 'data', etc.
├── requirements.txt        # Lista de todas as bibliotecas Python que seu projeto usa
└── README.md               # Documentação completa do projeto



1- python -m venv venv
2- .\venv\Scripts\activate (ou source venv/bin/activate no linux/mac)
3- pip install -r requirements.txt
4- exec webscrapping - python scripts/scrape_books.py
5- Chama api - python api/app.py



http://127.0.0.1:5000/
Export - data/books.csv
http://127.0.0.1:5000/docs/


Usuário: admin
Senha: adminpass (ou a senha que você configurar na variável de ambiente ADMIN_PASSWORD)


/api/v1/books, /api/v1/books/{id}, /api/v1/books/search, /api/v1/categories, /api/v1/health



Curl no terminal ou softwares como Postman/Insomnia para testar:
# Exemplo com curl para /api/v1/health
curl -u admin:adminpass http://127.0.0.1:5000/api/v1/health

# Exemplo com curl para /api/v1/books
curl -u admin:adminpass http://127.0.0.1:5000/api/v1/books

# Exemplo com curl para /api/v1/books/search
curl -u admin:adminpass "http://127.0.0.1:5000/api/v1/books/search?title=light&category=Poetry"