from django.shortcuts import render, redirect
from django.core.files.base import ContentFile
from django.views.generic import DetailView, ListView
from django.contrib.postgres.search import TrigramSimilarity

import requests
from bs4 import BeautifulSoup

from .models import Card
from .forms import SearchForm

class ShoesView(ListView):
    model = Card
    template_name = 'parser/list.html'
    context_object_name = 'cards'
    paginate_by = 36

    def get_queryset(self):
        queryset = Card.objects.all()

        search_query = self.request.GET.get('search_query')
        if search_query:
            queryset = queryset.annotate(similarity=TrigramSimilarity('name', search_query))
            queryset = queryset.filter(similarity__gt=0.05)
            
        sort = self.request.GET.get('sort', 'price')
        if sort == 'price':
            queryset = queryset.order_by('price')
        elif sort == '-price':
            queryset = queryset.order_by('-price')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sort = self.request.GET.get('sort', 'price')
        context['sort'] = sort
        context['search_form'] = SearchForm(self.request.GET)
        return context

class CardDetailView(DetailView):
    model = Card
    template_name = 'parser/detail.html'
    context_object_name = 'card'
    slug_url_kwarg = 'card_slug'


def is_page_not_found(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    not_found_message = 'Ми не можемо знайти продукти, що відповідають вибору'
    return not_found_message in soup.get_text().lower()


def update(request):
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }
    current_page = 1
    base_url = 'https://ua.puma.com/uk/sportivnye-tovary-dlja-muzhchin/obuv.html'
    page = '?p='

    print('Начался процесс сбора данных. Чтобы остановить его, перезапустите сервер')

    while True:
        url = f'{base_url}{page}{current_page}'
        req = requests.get(url, headers=headers)
        if is_page_not_found(req.text) or current_page == 17:  # потом убрать
            print(f'Ми не можемо знайти продукти, що відповідають вибору на странице')
            break
        soup = BeautifulSoup(req.text, 'html.parser')
        cards = soup.find_all(class_='grid__item image-sv01')

        for card in cards:
            name = card.find('a', class_='product-item__name').text.strip()
            price = int(card.find('span', class_='price').text.replace(
                ' ', '').replace('₴', '').replace('\n', '').strip().split(",")[0])
            link = card.find('a', class_='product-item__img-w').get('href')

            if not Card.objects.filter(link=link).exists():
                card = Card(name=name, price=price, link=link)
                card.save()
                response_detail = requests.get(link, headers=headers)
                soup_detail = BeautifulSoup(
                    response_detail.text, 'html.parser')
                img_url = soup_detail.find(
                    'img', class_='gallery-item__img').get('src')
                image_content = requests.get(img_url).content
                image_file = ContentFile(image_content)
                image_file.name = f'{card.slug}.png'
                card.photo = image_file
                card.save()
        current_page += 1
        print(current_page)
    return redirect('shoes_list')

# def update_detail_info():
#     headers = {
#         'Accept': '*/*',
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
#     }
#     cards = Card.objects.all()
#     for card in cards:
#         link = card.link
#         req = requests.get(link, headers=headers)
#         soup = BeautifulSoup(req.text, 'html.parser')
#         description = soup.find('p').text
#         card.description = description
#         card.save()
