import pytest
from models.product_model import Category
from schemas.product_schema import CreateCategoryRequest
from models.user_model import User


def test_create_category(client, db_session, token):
    category_data = CreateCategoryRequest(id=0, name="Test Category")
    response = client.post("/category/create-category/", headers={"Authorization": 'Bearer ' + token}, json=category_data.model_dump())
    assert response.status_code == 201
    assert response.json()["data"][Category.__name__]["name"] == category_data.name

def test_create_category(client, db_session, token):
    category_data = CreateCategoryRequest(id=0, name="Test Category")
    response = client.post("/category/create-category/", headers={"Authorization": 'Bearer ' + token}, json=category_data.model_dump())
    assert response.status_code == 201
    assert response.json()["data"][Category.__name__]["name"] == category_data.name

def test_list_categories(client, db_session, token):
    response = client.get("/category/list-categories/", headers={"Authorization": 'Bearer ' + token})
    assert response.status_code == 200

def test_get_category(client, db_session, token):
    category = Category(name="Test Category")
    db_session.add(category)
    db_session.commit()
    response = client.get(f"/category/get-category/{category.id}/", headers={"Authorization": 'Bearer ' + token})
    db_session.close()
    assert response.status_code == 200

def test_update_category(client, db_session, token):
    category = Category(name="Test Category")
    db_session.add(category)
    db_session.commit()
    updated_category_data = CreateCategoryRequest(id= category.id, name="Updated Category")
    response = client.put("/category/update-category", headers={"Authorization": 'Bearer ' + token}, json=updated_category_data.model_dump())
    db_session.close()
    assert response.status_code == 200

def test_delete_category(client, db_session, token):
    category = Category(name="Test Category")
    db_session.add(category)
    db_session.commit()
    response = client.delete(f"/category/delete-category/{category.id}/", headers={"Authorization": 'Bearer ' + token})
    assert response.status_code == 200
