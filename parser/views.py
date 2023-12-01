from django.views import View
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils.text import slugify

import requests
from bs4 import BeautifulSoup

from .models import Card

class ShoesView(View):
    template_name = 'parser/list.html'
    items_per_page = 36

    def get(self, request, *args, **kwargs):

        page_number = request.GET.get('page', 1)
        cards = Card.objects.all()
        paginator = Paginator(cards, self.items_per_page)
        page_obj = paginator.get_page(page_number)
        context = {'page_obj': page_obj, 'current_page': page_obj.number}
        return render(request, self.template_name, context)
    
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

    while True:
        url = f'{base_url}{page}{current_page}'
        req = requests.get(url, headers=headers)
        if is_page_not_found(req.text) or current_page==17: # потом убрать
            print(f'Ми не можемо знайти продукти, що відповідають вибору на странице')
            break
        soup = BeautifulSoup(req.text, 'html.parser')
        cards = soup.find_all(class_='grid__item image-sv01')

        for card in cards:
            name = card.find('a', class_='product-item__name').text.strip()
            price = int(card.find('span', class_='price').text.replace(' ', '').replace('₴', '').replace('\n', '').strip().split(",")[0])
            link = card.find('a', class_='product-item__img-w').get('href')

            if not Card.objects.filter(link=link).exists():
                card = Card(name=name, price=price, link=link)
                card.save()
                # print(current_page)
                # response_detail = requests.get(link, headers=headers)
                # soup_detail= BeautifulSoup(response_detail.text, 'html.parser')
                # img_url = soup_detail.find('img', class_='gallery-item__img').get('src')
                # image_content = requests.get(img_url).content
                # image_file = ContentFile(image_content)
                # image_file.name = f'{card.slug}.png'
                # card.photo = image_file
                # card.save()
        current_page += 1
    return redirect('shoes_list')
