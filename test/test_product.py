import pytest
from models.product_model import Category, ProductDeal
from schemas.product_schema import CreateProductDealRequest
from datetime import datetime
def test_load_products_by_category(client, db_session, token):
    category = Category(name="Test Category")
    db_session.add(category)
    db_session.commit()

    response = client.post(
        "/product/load-products-by-category/?category_id=1",
        headers={"Authorization": 'Bearer ' + token},
        files={"file": ("test/data_test.csv", open("test/data_test.csv", "rb"))},
    )
    
    assert response.status_code == 201

def test_list_products(client, db_session, token):
    response = client.get("/product/list-products/", headers={"Authorization": 'Bearer ' + token})
    assert response.status_code == 200
    assert "current_page" in response.json()['additional_data']
    assert "limit_per_page" in response.json()['additional_data']
    assert "item_per_page" in response.json()['additional_data']
    assert "next_page" in response.json()['additional_data']
    assert "previous_page" in response.json()['additional_data']
    assert "total_items" in response.json()['additional_data']

def test_deactivate_all_products(client, db_session, token):
    response = client.put("/product/products/deactivate-all-by-date/", headers={"Authorization": 'Bearer ' + token})
    assert response.status_code == 200
    assert "message" in response.json()

def test_delete_product_by_id(client, db_session, token):
    product = ProductDeal(title="Test Product", category_id=1, price=10.0, total_rating=5, img="http://testimg.com", discount=10, url="http://test.com")
    db_session.add(product)
    db_session.commit()
    response = client.put("/product/delete-product-by-id/?product_id=1", headers={"Authorization": 'Bearer ' + token})
    assert response.status_code == 200
    assert "data" in response.json()

def test_delete_product_by_date(client, db_session, token):
    product = ProductDeal(title="Test Product", category_id=1, price=10.0, total_rating=5, img="http://testimg.com", discount=10, url="http://test.com")
    db_session.add(product)
    db_session.commit()
    response = client.put("/product/delete-product-by-date/", headers={"Authorization": 'Bearer ' + token})
    assert response.status_code == 200
    assert "message" in response.json()

def test_create_product(client, db_session, token):
    category = Category(name="Test Category")
    db_session.add(category)
    db_session.commit()
    product_data = {
        'id':0, 
        'title':"Test Product", 
        'category_id':1, 
        'price':10.0, 
        'total_rating':5, 
        'img':"http://testimg.com", 
        'discount':10, 
        'url':"http://test.com", 
        'date':datetime.now().date().isoformat()
        }
    response = client.post("/product/create-product/", headers={"Authorization": 'Bearer ' + token}, json=product_data)
    print(response.json())
    assert response.status_code == 201
    assert "data" in response.json()

def test_get_product_by_id(client, db_session, token):
    product = ProductDeal(title="Test Product", category_id=1, price=10.0, total_rating=5, img="http://testimg.com", discount=10, url="http://test.com")
    db_session.add(product)
    db_session.commit()
    response = client.get("/product/get-product-by-id/",  headers={"Authorization": 'Bearer ' + token}, params={"product_id": 1})
    print(response.json())
    assert response.status_code == 200
    assert "data" in response.json()

def test_get_product_by_category(client, db_session, token):
    response = client.get("/product/get-product-by-category/", headers={"Authorization": 'Bearer ' + token}, params={"category_id": 1})
    assert response.status_code == 200
    assert "current_page" in response.json()['additional_data']
    assert "limit_per_page" in response.json()['additional_data']
    assert "item_per_page" in response.json()['additional_data']
    assert "next_page" in response.json()['additional_data']
    assert "previous_page" in response.json()['additional_data']
    assert "total_items" in response.json()['additional_data']

def test_get_product_by_discount(client, db_session, token):
    response = client.get("/product/get-product-by-discount/", headers={"Authorization": 'Bearer ' + token})
    assert response.status_code == 200
    assert "current_page" in response.json()['additional_data']
    assert "limit_per_page" in response.json()['additional_data']
    assert "item_per_page" in response.json()['additional_data']
    assert "next_page" in response.json()['additional_data']
    assert "previous_page" in response.json()['additional_data']
    assert "total_items" in response.json()['additional_data']

