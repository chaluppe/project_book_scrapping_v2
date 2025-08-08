
# Fonte:
https://books.toscrape.com/  <br>

# Documentação completa
https://docs.google.com/document/d/1EAfve-J_WsHJ7hdbWJ7fMKf15a91eqN-qnSc4OjGArk/edit?usp=sharing

<br>

# Estrutura
project_book_scrapping/ <br>
├── data/ <br>
│   └── books.csv - [Arquivo gerado pelo seu script de scraping] <br>
├── scripts/ <br>
│   └── scrape_books.py - [Código de scraping] <br>
├── api/ <br>
│   └── app.py - [Aplicação Flask] <br>
├── .gitignore - [Arquivo para o Git ignorar] <br>
├── requirements.txt - [Lista de todas as bibliotecas] <br>
└── README.md - [Documentação do projeto] <br>

<br>
<br>

# Sequencia de execução
1- py -3.11 -m venv venv  <br>
2- .\venv\Scripts\activate (ou source venv/bin/activate no linux/mac)  <br>
3- pip install -r requirements.txt  <br>
4- exec webscrapping - python scripts/scrape_books.py  <br>
5- [Chama api] - python api/app.py  <br>

<br>
<br>

# Detalhes
http://127.0.0.1:5000/  <br>
Export - data/books.csv  <br>
http://127.0.0.1:5000/docs/  <br>
Render Deploy - https://project-book-scrapping-v2.onrender.com <br>
Render - https://dashboard.render.com/web/srv-d232k1ngi27c73fgrfug <br>

<br>
<br>

# Logins
Usuário: admin  <br>
Senha: adminpass (ou a senha que você configurar na variável de ambiente ADMIN_PASSWORD)  <br>
<br>

Senha Render: 2701 ou 2309

<br>
<br>

# Postman
Curl no terminal ou softwares como Postman/Insomnia para testar:
curl -u admin:adminpass http://127.0.0.1:5000/api/v1/health

# Exemplo com curl para /api/v1/books
curl -u admin:adminpass http://127.0.0.1:5000/api/v1/books

# Exemplo com curl para /api/v1/books/search
curl -u admin:adminpass "http://127.0.0.1:5000/api/v1/books/search?title=light&category=Poetry"

<br>
<br>
