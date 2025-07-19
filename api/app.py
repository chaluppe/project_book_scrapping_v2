# api/app.py

from flask import Flask, jsonify, request
from flask_httpauth import HTTPBasicAuth
from flasgger import Swagger
import pandas as pd
import os
import secrets # Para gerar token de API ou senhas seguras
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# --- Configuração do Swagger ---
app.config['SWAGGER'] = {
    'title': 'API de Consulta de Livros',
    'uiversion': 3,
    'description': 'API para consulta de dados de livros, extraídos de books.toscrape.com, com foco em escalabilidade e reusabilidade para Machine Learning.',
    'version': '1.0.0',
    'specs_route': '/docs/' # Rota para a documentação
}
swagger = Swagger(app)

# --- Autenticação Básica ---
auth = HTTPBasicAuth()

# Usuários em memória (em um ambiente de produção, use um banco de dados ou serviço de autenticação)
USERS = {
    "admin": generate_password_hash(os.environ.get("ADMIN_PASSWORD", "adminpass")), # Use variáveis de ambiente!
    "user": generate_password_hash(os.environ.get("USER_PASSWORD", "userpass"))
}

@auth.verify_password
def verify_password(username, password):
    if username in USERS and check_password_hash(USERS.get(username), password):
        return username
    return None

# --- Carregamento de Dados ---
BOOKS_DATA = pd.DataFrame() # DataFrame global para armazenar os dados dos livros
DATA_FILE_PATH = os.path.join('data', 'books.csv') # Caminho para o arquivo CSV, relativo à raiz do projeto

def load_books_data():
    """Carrega os dados dos livros do CSV para a memória."""
    global BOOKS_DATA
    # Navega para o diretório raiz do projeto para encontrar 'data/books.csv'
    # Isso é importante para o deploy onde o diretório de trabalho pode ser diferente
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_data_path = os.path.join(project_root, DATA_FILE_PATH)

    if os.path.exists(full_data_path):
        try:
            BOOKS_DATA = pd.read_csv(full_data_path)
            # Converte 'id' para int, se não for
            if 'id' in BOOKS_DATA.columns:
                BOOKS_DATA['id'] = BOOKS_DATA['id'].astype(int)
            print(f"Dados de livros carregados com sucesso: {len(BOOKS_DATA)} registros.")
        except Exception as e:
            print(f"Erro ao carregar dados do CSV: {e}")
            BOOKS_DATA = pd.DataFrame() # Garante um DataFrame vazio em caso de erro
    else:
        print(f"Arquivo de dados '{full_data_path}' não encontrado. Execute 'python scripts/scrape_books.py' primeiro.")
        BOOKS_DATA = pd.DataFrame()

# Carrega os dados na inicialização da aplicação
with app.app_context():
    load_books_data()

# --- Endpoints da API (conforme o código anterior) ---

@app.route('/', methods=['GET'])
def home():
    """
    Endpoint de Boas-Vindas da API.
    ---
    responses:
      200:
        description: Mensagem de boas-vindas.
    """
    return jsonify({"message": "Bem-vindo à API de Consulta de Livros!"})

@app.route('/api/v1/health', methods=['GET'])
@auth.login_required
def health_check():
    """
    Verifica o status da API e a conectividade com os dados.
    ---
    security:
      - basicAuth: []
    responses:
      200:
        description: Status da API e dados carregados.
        schema:
          type: object
          properties:
            status:
              type: string
              example: UP
            data_loaded:
              type: boolean
              example: true
            num_books:
              type: integer
              example: 1000
      401:
        description: Não autorizado.
    """
    data_loaded = not BOOKS_DATA.empty
    return jsonify({
        "status": "UP",
        "data_loaded": data_loaded,
        "num_books": len(BOOKS_DATA) if data_loaded else 0
    })

@app.route('/api/v1/books', methods=['GET'])
@auth.login_required
def get_all_books():
    """
    Lista todos os livros disponíveis na base de dados.
    ---
    security:
      - basicAuth: []
    responses:
      200:
        description: Lista de livros.
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer, example: 1}
              title: {type: string, example: "A Light in the Attic"}
              price: {type: number, format: float, example: 51.77}
              rating: {type: integer, example: 3}
              availability: {type: boolean, example: true}
              category: {type: string, example: "Poetry"}
              image_url: {type: string, example: "http://books.toscrape.com/media/cache/fe/72/..."}
      401:
        description: Não autorizado.
      500:
        description: Erro interno do servidor se os dados não puderem ser carregados.
    """
    if BOOKS_DATA.empty:
        return jsonify({"message": "Dados de livros não disponíveis ou não carregados."}), 500

    books_list = BOOKS_DATA.to_dict(orient='records')
    return jsonify(books_list)

@app.route('/api/v1/books/<int:book_id>', methods=['GET'])
@auth.login_required
def get_book_by_id(book_id):
    """
    Retorna detalhes completos de um livro específico pelo ID.
    ---
    security:
      - basicAuth: []
    parameters:
      - name: book_id
        in: path
        type: integer
        required: true
        description: ID único do livro.
    responses:
      200:
        description: Detalhes do livro.
        schema:
          type: object
          properties:
            id: {type: integer, example: 1}
            title: {type: string, example: "A Light in the Attic"}
            price: {type: number, format: float, example: 51.77}
            rating: {type: integer, example: 3}
            availability: {type: boolean, example: true}
            category: {type: string, example: "Poetry"}
            image_url: {type: string, example: "http://books.toscrape.com/media/cache/fe/72/..."}
      401:
        description: Não autorizado.
      404:
        description: Livro não encontrado.
      500:
        description: Erro interno do servidor.
    """
    if BOOKS_DATA.empty:
        return jsonify({"message": "Dados de livros não disponíveis."}), 500

    book = BOOKS_DATA[BOOKS_DATA['id'] == book_id]
    if not book.empty:
        return jsonify(book.iloc[0].to_dict())
    return jsonify({"message": "Livro não encontrado."}), 404

@app.route('/api/v1/books/search', methods=['GET'])
@auth.login_required
def search_books():
    """
    Busca livros por título e/ou categoria.
    ---
    security:
      - basicAuth: []
    parameters:
      - name: title
        in: query
        type: string
        required: false
        description: Título (ou parte do título) do livro para buscar.
      - name: category
        in: query
        type: string
        required: false
        description: Categoria do livro para buscar.
    responses:
      200:
        description: Lista de livros que correspondem aos critérios de busca.
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer, example: 1}
              title: {type: string, example: "A Light in the Attic"}
              price: {type: number, format: float, example: 51.77}
              rating: {type: integer, example: 3}
              availability: {type: boolean, example: true}
              category: {type: string, example: "Poetry"}
              image_url: {type: string, example: "http://books.toscrape.com/media/cache/fe/72/..."}
      401:
        description: Não autorizado.
      500:
        description: Erro interno do servidor.
    """
    if BOOKS_DATA.empty:
        return jsonify({"message": "Dados de livros não disponíveis."}), 500

    title_query = request.args.get('title', '').strip().lower()
    category_query = request.args.get('category', '').strip().lower()

    filtered_books = BOOKS_DATA.copy()

    if title_query:
        filtered_books = filtered_books[
            filtered_books['title'].str.lower().str.contains(title_query, na=False)
        ]

    if category_query:
        filtered_books = filtered_books[
            filtered_books['category'].str.lower() == category_query
        ]

    if filtered_books.empty:
        return jsonify({"message": "Nenhum livro encontrado com os critérios fornecidos."}), 200

    return jsonify(filtered_books.to_dict(orient='records'))

@app.route('/api/v1/categories', methods=['GET'])
@auth.login_required
def get_categories():
    """
    Lista todas as categorias de livros disponíveis.
    ---
    security:
      - basicAuth: []
    responses:
      200:
        description: Lista de categorias únicas.
        schema:
          type: array
          items:
            type: string
            example: "Travel"
      401:
        description: Não autorizado.
      500:
        description: Erro interno do servidor.
    """
    if BOOKS_DATA.empty:
        return jsonify({"message": "Dados de livros não disponíveis."}), 500

    categories = BOOKS_DATA['category'].dropna().unique().tolist()
    categories.sort()
    return jsonify(categories)

# --- Endpoints Opcionais (Insights) ---

@app.route('/api/v1/stats/overview', methods=['GET'])
@auth.login_required
def get_stats_overview():
    """
    Estatísticas gerais da coleção (total de livros, preço médio, distribuição de ratings).
    ---
    security:
      - basicAuth: []
    responses:
      200:
        description: Estatísticas gerais.
        schema:
          type: object
          properties:
            total_books: {type: integer, example: 1000}
            average_price: {type: number, format: float, example: 35.50}
            rating_distribution:
              type: object
              properties:
                1_star: {type: integer, example: 50}
                2_star: {type: integer, example: 100}
                3_star: {type: integer, example: 200}
                4_star: {type: integer, example: 300}
                5_star: {type: integer, example: 350}
      401:
        description: Não autorizado.
      500:
        description: Erro interno do servidor.
    """
    if BOOKS_DATA.empty:
        return jsonify({"message": "Dados de livros não disponíveis."}), 500

    total_books = len(BOOKS_DATA)
    average_price = BOOKS_DATA['price'].mean()

    rating_counts = BOOKS_DATA['rating'].value_counts().to_dict()
    rating_distribution = {f"{k}_star": rating_counts.get(k, 0) for k in range(1, 6)}

    return jsonify({
        "total_books": total_books,
        "average_price": round(average_price, 2),
        "rating_distribution": rating_distribution
    })

@app.route('/api/v1/stats/categories', methods=['GET'])
@auth.login_required
def get_stats_categories():
    """
    Estatísticas detalhadas por categoria (quantidade de livros, preços por categoria).
    ---
    security:
      - basicAuth: []
    responses:
      200:
        description: Estatísticas por categoria.
        schema:
          type: array
          items:
            type: object
            properties:
              category_name: {type: string, example: "Travel"}
              book_count: {type: integer, example: 10}
              average_price: {type: number, format: float, example: 40.25}
              top_rated_book_in_category: {type: string, example: "The book with 5 stars"}
      401:
        description: Não autorizado.
      500:
        description: Erro interno do servidor.
    """
    if BOOKS_DATA.empty:
        return jsonify({"message": "Dados de livros não disponíveis."}), 500

    category_stats = []
    for category_name, group in BOOKS_DATA.dropna(subset=['category']).groupby('category'):
        book_count = len(group)
        average_price = group['price'].mean()

        top_rated_book = None
        if not group.empty:
            top_rated_book_df = group.sort_values(by=['rating', 'price'], ascending=[False, True]).iloc[0]
            top_rated_book = top_rated_book_df['title']

        category_stats.append({
            "category_name": category_name,
            "book_count": book_count,
            "average_price": round(average_price, 2),
            "top_rated_book_in_category": top_rated_book
        })

    category_stats.sort(key=lambda x: x['category_name'])

    return jsonify(category_stats)

@app.route('/api/v1/books/top-rated', methods=['GET'])
@auth.login_required
def get_top_rated_books():
    """
    Lista os livros com melhor avaliação (rating mais alto).
    ---
    security:
      - basicAuth: []
    responses:
      200:
        description: Lista de livros com melhor avaliação.
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer, example: 1}
              title: {type: string, example: "A Light in the Attic"}
              rating: {type: integer, example: 5}
              price: {type: number, format: float, example: 51.77}
      401:
        description: Não autorizado.
      500:
        description: Erro interno do servidor.
    """
    if BOOKS_DATA.empty:
        return jsonify({"message": "Dados de livros não disponíveis."}), 500

    max_rating = BOOKS_DATA['rating'].max()
    top_rated_books = BOOKS_DATA[BOOKS_DATA['rating'] == max_rating].sort_values(by='price', ascending=True)

    return jsonify(top_rated_books.to_dict(orient='records'))

@app.route('/api/v1/books/price-range', methods=['GET'])
@auth.login_required
def get_books_by_price_range():
    """
    Filtra livros dentro de uma faixa de preço específica.
    ---
    security:
      - basicAuth: []
    parameters:
      - name: min
        in: query
        type: number
        format: float
        required: true
        description: Preço mínimo da faixa.
      - name: max
        in: query
        type: number
        format: float
        required: true
        description: Preço máximo da faixa.
    responses:
      200:
        description: Lista de livros dentro da faixa de preço.
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer, example: 1}
              title: {type: string, example: "A Light in the Attic"}
              price: {type: number, format: float, example: 51.77}
      400:
        description: Parâmetros de preço inválidos.
      401:
        description: Não autorizado.
      500:
        description: Erro interno do servidor.
    """
    if BOOKS_DATA.empty:
        return jsonify({"message": "Dados de livros não disponíveis."}), 500

    try:
        min_price = float(request.args.get('min'))
        max_price = float(request.args.get('max'))
    except (ValueError, TypeError):
        return jsonify({"message": "Parâmetros 'min' e 'max' devem ser números válidos."}), 400

    if min_price is None or max_price is None:
        return jsonify({"message": "Os parâmetros 'min' e 'max' são obrigatórios."}), 400

    filtered_books = BOOKS_DATA[
        (BOOKS_DATA['price'] >= min_price) & 
        (BOOKS_DATA['price'] <= max_price)
    ].to_dict(orient='records')

    if not filtered_books:
        return jsonify({"message": "Nenhum livro encontrado na faixa de preço especificada."}), 200

    return jsonify(filtered_books)


# --- Execução da Aplicação ---
if __name__ == '__main__':
    # Em produção, não use debug=True e configure o host/port
    # Use um servidor WSGI como Gunicorn ou Waitress para deploy
    app.run(debug=True, host='0.0.0.0', port=5000)