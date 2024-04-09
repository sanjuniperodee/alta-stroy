import os
import re

import requests
from .models import *
from django.conf import settings
from django.core.files.storage import default_storage
from django.db.models import Q

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.core.files.base import ContentFile
from requests import get
from django.db.models import Count
from django.db.models import Min
from django.db.models import Subquery





# stripe.api_key = settings.STRIPE_SECRET_KEY

def home(request):
    articul = request.GET.get('articul')
    if articul:
        return redirect(f'/shop/all/all?articul={articul}')
    portfolio = Portfolio.objects.all()
    partners = Partners.objects.all()
    bests = Item.objects.filter(sales=True)
    return render(request, 'index.html', {'categories': Category.objects.all(), 'bests': bests, 'portfolio':portfolio, 'partners':partners,})

# def parket(request):
#     return render(request, 'parket.html', {'subcategories': SubCategory.objects.filter(is_parket=True)})

def shop(request, ctg, ctg2):
    categories = set(Category.objects.all())
    subcategory = ctg2
    articul = request.GET.get('articul')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if ctg2 != 'all' and ctg !='all':
        category = Category.objects.filter(title=ctg)[0]
        object_list = Item.objects.filter(category__title=ctg, subcategory__title=ctg2)
        subcategory = SubCategory.objects.filter(title=ctg2).first()
    elif ctg2 == 'all' and ctg !='all':
        category = Category.objects.filter(title=ctg)[0]
        object_list = Item.objects.filter(category__title=ctg)
        subcategory = None
    else:
        category = 'all'
        object_list = Item.objects.all()
    if articul:
        object_list = object_list.filter(Q(articul__icontains=articul) | Q(title__icontains=articul))
        if ctg == 'all':
            categories = set()
            for item in object_list:
                categories.add(item.category)
    if min_price and max_price:
        object_list = object_list.filter(price__gte=min_price, price__lte=max_price)
    paginator = Paginator(object_list, 18)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    pagination_links = []
    for page in page_obj.paginator.page_range:
        query_parameters = request.GET.copy()
        query_parameters['page'] = page
        pagination_links.append({'page_number': page, 'query_parameters': query_parameters.urlencode()})
    pages = int(len(object_list)/18)
    if len(object_list) % 18 > 0:
        pages+=1
    print(subcategory)
    print(123123123)
    context = {
        'min_price': min_price,
        'max_price': max_price,
        'subcategory' : subcategory,
        'categories': categories,
        'pages': range(1,pages+1),
        'category': category,
        'items': page_obj,
        'user': request.user,
        'pagination_links': pagination_links,
    }
    return render(request, 'shop.html', context)

def detail(request, slug):
    item = Item.objects.filter(slug=slug)[0]
    photos = ItemImage.objects.filter(post=item)
    try:
        description1 = item.description1.split('\n')
        description2 = item.description2.split('\n')
    except:
        description1 = ''
        description2 = ''
    context = {
        'item': item,
        'description1': description1,
        'description2': description2,
        'categories': Category.objects.all(),
        'photos': photos,
    }
    return render(request, 'detail.html', context)


@login_required
def add_to_cart1(request):
    print(12312)
    slug = str(request.POST.get('slug'))
    print(slug)
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, payment=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
        else:
            order.items.add(order_item)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
    return JsonResponse({'data': '123'})

@login_required
def cart(request):
    try:
        order = Order.objects.filter(user=request.user, payment=False)[0]
    except:
        order = Order.objects.create(user=request.user, payment=False)
    print(request.user)
    context = {
        'order': order,
        'categories': Category.objects.all()
    }
    return render(request, 'cart.html', context)

@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        payment=False,
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            return redirect("core:cart")
        else:
            return redirect("core:detail", slug=slug)
    else:
        return redirect("core:detail", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        payment=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            return redirect("core:cart")
        else:
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)

@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False

    )
    order_qs = Order.objects.filter(user=request.user, payment=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            return redirect("core:cart")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("core:cart")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("core:order-summary")


@login_required
def profile(request):
    if request.method == "POST":
        cnt = 0
        if len(UserProfile.objects.filter(user__username=request.POST['username'])) > 0 and request.POST[
            'username'] != request.user.username:
            # messages.info(request, 'User already exists')
            cnt = 1
        if len(request.POST['password1']) > 0:
            if len(request.POST['password1']) < 8:
                # messages.info(request, 'Password must contain at least 8 symbols')
                cnt = 1
            if len(request.POST['password1']) and len(request.POST['password2']) and request.POST['password1'] != \
                    request.POST['password2']:
                # messages.info(request, 'Password not matching')
                cnt = 1
            if len(request.POST['password1']) < 8 and request.POST['password1'] == request.POST['password2']:
                pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).+$'
                if not re.match(pattern, password1):
                    # messages.info(request, "Password must contain at least 1 uppercase, 1 lowercase and one number")
                    cnt = 1
        if cnt == 1:
            return redirect('core:profile')
        else:
            if len(request.POST['password1']) > 0 and len(request.POST['password2']) > 0:
                request.user.password1 = request.POST['password1']
                request.user.password2 = request.POST['password2']

            request.user.username = request.POST['username']
            request.user.email = request.POST['email']
            request.user.first_name = request.POST['first_name']
            request.user.last_name = request.POST['last_name']
            request.user.save()
            return redirect('core:profile')
    print(request.user.username)
    return render(request, 'profile.html', {'user': request.user,'categories': Category.objects.all()})


def about_us(request):
    return render(request, 'about_us.html', {'categories': Category.objects.all()})

def sales(request):
    object_list = Item.objects.filter(sales=True)
    paginator = Paginator(object_list, 18)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    pages = int(len(object_list) / 18)
    if len(object_list) % 18 > 0:
        pages += 1
    context = {
        'categories': Category.objects.all(),
        'pages': range(1, pages + 1),
        'category': 'Акции',
        'items': page_obj,
        'user': request.user,
    }
    return render(request, 'shop.html', context)


def new_items(request):
    object_list = Item.objects.filter(sales=True)
    paginator = Paginator(object_list, 18)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    pages = int(len(object_list) / 18)
    if len(object_list) % 18 > 0:
        pages += 1
    context = {
        'pages': range(1, pages + 1),
        'category': 'Новинки',
        'items': page_obj,
        'user': request.user,
    }
    return render(request, 'shop.html', context)

def delete_duplicates(request):
    duplicate_names = Item.objects.values_list('articul', flat=True).distinct()

    for email in duplicate_names:
        Item.objects.filter(pk__in=Item.objects.filter(articul=email).values_list('pk', flat=True)[1:]).delete()

# def change_prices(request):
#     for item in Item.objects.all():
#         item.price = item.price/6.5 * 5.5
#         item.save()

def greenline(request):
    href = 'https://parket-greenline.ru'
    soup = BeautifulSoup(get(href+'/products/inzhenernaya-doska/smart/').text, 'html.parser')
    items = soup.find_all('div', class_='item_4')
    for item in items:
        page = BeautifulSoup(get(href+item.find('a')['href']).text, 'html.parser')
        print(href+'/products/inzhenernaya-doska/smart'+item.find('a')['href'])
        title = page.find('h1', class_='bx-title').text.strip()
        print(title)
        table = page.find('dl', class_='product-item-detail-properties')
        for row in table:
            value = row.find('dt').text
            key = row.find('dd').text
            if key == 'Коллекция':
                collection = key
            # if key == 'Декор':

        break


def slug(request):
    for item in Item.objects.all():
        try:
            item.slug = item.slug.replace('/', '_')
            item.save()
        except:
            item.slug = item.pk
