# scripts/scrape_books.py

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import os
from urllib.parse import urljoin # Importar urljoin para uma melhor combinação de URLs

def clean_price(price_text):
    """Extrai o valor numérico do texto do preço."""
    match = re.search(r'[\d\.]+', price_text)
    if match:
        return float(match.group())
    return 0.0

def get_star_rating(rating_class):
    """Converte a classe CSS de rating para um valor numérico."""
    rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
    return rating_map.get(rating_class, 0)

# Função para extrair categoria da página de detalhes (se necessário e implementado)
# Por enquanto, vou manter o placeholder 'N/A' como no seu código original
def scrape_category_from_detail_page(book_detail_url):
    # Esta função é para uma melhoria futura ou se a categoria não estiver na página principal.
    # Por simplicidade, mantemos 'N/A' como no seu código.
    # No entanto, para atender completamente ao requisito, você precisaria implementá-la.
    # Ex: return "Travel"
    return "N/A" # Placeholder atual

def scrape_books_to_csv(base_url="https://books.toscrape.com/", output_dir="data"):
    all_books_data = []
    current_page_url = base_url
    book_id_counter = 1 # Adiciona um contador de ID

    print("Iniciando scraping...")
    # Garante que a pasta 'data' exista
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    while current_page_url:
        try:
            print(f"Raspando página: {current_page_url}")
            response = requests.get(current_page_url, timeout=10) # Adicionei timeout
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            books = soup.find_all('article', class_='product_pod')

            for book in books:
                title_element = book.h3.a
                title = title_element['title'].strip() if title_element and 'title' in title_element.attrs else "N/A"

                # URL de detalhes do livro para possível extração de categoria (se implementado)
                book_detail_relative_url = title_element['href'] if title_element and 'href' in title_element.attrs else ""
                # Use current_page_url como base para urljoin para links de detalhes
                book_detail_full_url = urljoin(current_page_url, book_detail_relative_url)


                price_text = book.find('p', class_='price_color').text
                price = clean_price(price_text) # Usa a função auxiliar

                rating_class = book.find('p', class_='star-rating')['class'][1]
                rating = get_star_rating(rating_class) # Usa a função auxiliar

                availability_text = book.find('p', class_='instock availability').text.strip()
                availability = 'In stock' in availability_text

                image_element = book.find('img')
                image_url_relative = image_element['src'] if image_element and 'src' in image_element.attrs else ""
                # Use current_page_url como base para urljoin para URLs de imagem
                full_image_url = urljoin(current_page_url, image_url_relative)

                # A chamada para obter a categoria (mantendo 'N/A' por enquanto)
                category = scrape_category_from_detail_page(book_detail_full_url) # Usaria esta função se a implementasse

                all_books_data.append({
                    'id': book_id_counter, # Adiciona o ID único
                    'title': title,
                    'price': price,
                    'rating': rating,
                    'availability': availability,
                    'category': category,
                    'image_url': full_image_url,
                    'detail_url': book_detail_full_url # Adiciona a URL de detalhes
                })
                book_id_counter += 1

            next_button = soup.find('li', class_='next')
            if next_button and next_button.a and 'href' in next_button.a.attrs:
                next_page_relative_url = next_button.a['href']
                current_page_url = urljoin(current_page_url, next_page_relative_url)
                time.sleep(1)
            else:
                current_page_url = None

        except requests.exceptions.RequestException as e:
            print(f"Erro de requisição: {e}. Encerrando scraping desta página.")
            current_page_url = None # Encerra se houver erro grave de requisição
        except Exception as e:
            print(f"Um erro inesperado ocorreu: {e}. Encerrando scraping desta página.")
            current_page_url = None # Encerra se houver erro inesperado

    df = pd.DataFrame(all_books_data)
    output_path = os.path.join(output_dir, 'books.csv')
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Scraping concluído! {len(all_books_data)} livros salvos em {output_path}")

if __name__ == "__main__":
    scrape_books_to_csv()