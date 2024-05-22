import pytest

def test_load_products_by_category(client, db_session, token):
    response = client.post(
        "/product/load-products-by-category/?category_id=1",
        headers={"Authorization": 'Bearer ' + token},
        files={"file": ("test/data_test.csv", open("test/data_test.csv", "rb"))},
    )
    print(response.json())
    assert response.status_code == 201
    assert response.json()["message"] == "File successfully processed and a total of 10 data inserted into the database."


""" def test_list_products(client, db):
    # Test case for list_products endpoint
    response = client.get("/product/list-products/")
    assert response.status_code == 200
    assert "current_page" in response.json()
    assert "limit_per_page" in response.json()
    assert "item_per_page" in response.json()
    assert "next_page" in response.json()
    assert "previous_page" in response.json()
    assert "total_items" in response.json()

def test_deactivate_all_products(client, db):
    # Test case for deactivate_all_products endpoint
    response = client.put("/product/products/deactivate-all-by-date/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_delete_product_by_id(client, db):
    # Test case for delete_product_by_id endpoint
    response = client.put("/product/delete-product-by-id/", json={"product_id": 1})
    assert response.status_code == 200
    assert "data" in response.json()

def test_delete_product_by_date(client, db):
    # Test case for delete_product_by_date endpoint
    response = client.put("/product/delete-product-by-date/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_create_product(client, db):
    # Test case for create_product endpoint
    response = client.post("/product/create-product/", json={"name": "Test Product", "category_id": 1})
    assert response.status_code == 201
    assert "data" in response.json()

def test_get_product_by_id(client, db):
    # Test case for get_product_by_id endpoint
    response = client.get("/product/get-product-by-id/", params={"product_id": 1})
    assert response.status_code == 200
    assert "data" in response.json()

def test_get_product_by_category(client, db):
    # Test case for get_product_by_category endpoint
    response = client.get("/product/get-product-by-category/", params={"category_id": 1})
    assert response.status_code == 200
    assert "current_page" in response.json()
    assert "limit_per_page" in response.json()
    assert "item_per_page" in response.json()
    assert "next_page" in response.json()
    assert "previous_page" in response.json()
    assert "total_items" in response.json()

def test_get_product_by_discount(client, db):
    # Test case for get_product_by_discount endpoint
    response = client.get("/product/get-product-by-discount/")
    assert response.status_code == 200
    assert "current_page" in response.json()
    assert "limit_per_page" in response.json()
    assert "item_per_page" in response.json()
    assert "next_page" in response.json()
    assert "previous_page" in response.json()
    assert "total_items" in response.json()

def test_update_product(client, db):
    # Test case for update_product endpoint
    response = client.put("/product/update-product/", json={"id": 1, "name": "Updated Product"})
    assert response.status_code == 200
    assert "data" in response.json() """