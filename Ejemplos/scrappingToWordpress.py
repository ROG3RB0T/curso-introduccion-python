#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf8')
import requests
import bs4 as bs

from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc.methods import media, posts

def getCatalogos(url):
    try:
        print("Scrapping la url: "+url+"\n")
        page = 1
        r = requests.get(url+"?p="+str(page))
        soup = bs.BeautifulSoup(r.content, 'html.parser')
        category = soup.find('span',class_="category")
        print("Categoria: "+category.text.strip()+"\n")
        category = category.text.strip()
        filename = 'scrappingCuracao_' + category + '.csv'
        product_items = soup.find_all('div',class_="product-item-info")
        #f = open(filename, "wb")

        for product_info in product_items:
            img = product_info.find('img',class_="product-image-photo")
            img = img["src"]
            brand = product_info.find('strong',class_="product-item-category")
            if brand is not None:
                brand = brand.text.strip()
            else:
                brand = ''
            link = product_info.find('a',class_="product-item-link")
            name = link.text.strip()
            link = link["href"]
            price_box = product_info.find('div',class_="price-box")
            prices = price_box.find_all('span',class_="price-wrapper")
            old_price = ""
            final_price = ""

            if prices is not None:
                for price in prices:

                    if price["data-price-type"] == "oldPrice":
                        old_price = price["data-price-amount"]

                    if price["data-price-type"] == "finalPrice":
                        final_price = price["data-price-amount"]

            id = price_box["data-product-id"]

            print("<img width=\"200\" height=\"200\" src=\"" + str(img) + "\" /><br><strong>" + u''.join(name).encode('utf-8').strip() + "</strong><br><h1>Precio Anterior: " + str(old_price) + "</h1><br><h1>Nuevo Precio: " + str(final_price) + "</h1><br><a href=\"" + link + "\" target=\"_blank\" >Click Aqui</a>\n")

            wp = Client('http://35.193.40.235/xmlrpc.php', 'user', 'WG2RXkar0SGt')
            # Insert en el sistema wordpress
            post = WordPressPost()
            post.title = u''.join((str(name),"<img width=\"200\" height=\"200\" src=\""+str(img)+"\" />"))
            post.content = "<h1>Precio Anterior: "+str(old_price)+"</h1><br><h1>Nuevo Precio: "+str(final_price)+"</h1><br><a href=\""+link+"\" target=\"_blank\" >Click Aqui</a>"
            post.post_status = 'publish'
            post.terms_names = {'post_tag': ['demo-python'], 'category': [u''.join(category).encode('utf-8').strip()]}
            post.custom_fields = []
            post.custom_fields.append({'_demo': '1200'})
            wp.call(NewPost(post))

        pages = soup.find('li',class_="item pages-item-next")
        if pages != None:
            next_url = pages.a["href"]

            getCatalogos(next_url)


    except Exception as e:
        sys.exit(e)
try:
    urls = "https://www.lacuracaonline.com/elsalvador/productos"
    r = requests.get(urls)
    soup = bs.BeautifulSoup(r.content,"html.parser")
    subcategories = soup.find_all('li',class_="subcategory")
    for subcategory in subcategories:
        getCatalogos(subcategory.a["href"])

except Exception as e:
    sys.exit(e)

