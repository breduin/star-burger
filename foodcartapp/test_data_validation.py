"""
Test of validate_data_from_frontend() 
"""

from django.test import TestCase
from rest_framework import status
from .models import Product, ProductCategory
from .views import validate_data_from_frontend


class TestValidationFunction(TestCase):

    @classmethod
    def setUpTestData(cls):
        #Set up non-modified objects used by all test methods
        category = ProductCategory.objects.create(name='Роллы')
        Product.objects.create(category=category,
                               name='Бургер1',
                               price=369
                               )
        Product.objects.create(category=category,
                               name='Бургер2',
                               price=249
                               )


    def test_data_are_ok(self):
        product1 = Product.objects.get(name='Бургер1')
        product2 = Product.objects.get(name='Бургер2')
        
        data = {
            "products": [
                {"product": product1.id, 
                "quantity": 1
                },
                {"product": product2.id, 
                "quantity": 3
                },                
                ], 
            "firstname": "Vasya",
            "lastname": "Petrov",
            "address": "Дыбенко",
            "phonenumber": "+79311234567",
        }      
        error, error_status = validate_data_from_frontend(data)
        self.assertEqual(error, None)
        self.assertEqual(error_status, None)  


    def test_products_field_is_string(self):
        """
        Продукты — это не список, а строка.
        products: Ожидался list со значениями, но был получен "str".
        """
        data = {
            "products": "HelloWorld", 
            "firstname": "Vasya",
            "lastname": "Petrov",
            "address": "Дыбенко",
            "phonenumber": "+79311234567",
        }      
        error, error_status = validate_data_from_frontend(data)
        self.assertNotEqual(error, None)
        self.assertEqual(error_status, status.HTTP_406_NOT_ACCEPTABLE)


    def test_products_field_is_null(self):
        """
        Продукты — это null.
        products: Это поле не может быть пустым.
        """
        data = {
            "products": None, 
            "firstname": "Vasya",
            "lastname": "Petrov",
            "address": "Дыбенко",
            "phonenumber": "+79311234567",
        }      
        error, error_status = validate_data_from_frontend(data)
        self.assertNotEqual(error, None)
        self.assertEqual(error_status, status.HTTP_417_EXPECTATION_FAILED)


    def test_products_field_is_empty_list(self):
        """
        Продукты — пустой список.
        products: Этот список не может быть пустым.
        """
        data = {
            "products": [], 
            "firstname": "Vasya",
            "lastname": "Petrov",
            "address": "Дыбенко",
            "phonenumber": "+79311234567",
        }      
        error, error_status = validate_data_from_frontend(data)
        self.assertNotEqual(error, None)
        self.assertEqual(error_status, status.HTTP_417_EXPECTATION_FAILED)


    def test_products_field_lacks(self):
        """
        Продуктов нет.
        products: Обязательное поле.
        """
        data = {
            "firstname": "Vasya",
            "lastname": "Petrov",
            "address": "Дыбенко",
            "phonenumber": "+79311234567",
        }      
        error, error_status = validate_data_from_frontend(data)
        self.assertNotEqual(error, None)
        self.assertEqual(error_status, status.HTTP_417_EXPECTATION_FAILED)


    def test_product_does_not_exist(self):
        """
        Заказ с неуществующим id продукта.
        products: Недопустимый первичный ключ "9999"
        """
        product1 = Product.objects.get(name='Бургер1')
        product2 = Product.objects.get(name='Бургер2')

        data = {
            "products": [
                {"product": 9999, 
                "quantity": 1
                },
                {"product": product2.id, 
                "quantity": 3
                },                
                ], 
            "firstname":  "Vasya",
            "lastname": "Petrov",
            "address": "Дыбенко",
            "phonenumber": "+79311234567",
        }      
        error, error_status = validate_data_from_frontend(data)
        self.assertNotEqual(error, None)
        self.assertEqual(error_status, status.HTTP_404_NOT_FOUND)


    def test_products_keys_lack(self):
        """
        Нет ключа product в списке products.
        products: 
        """
        product1 = Product.objects.get(name='Бургер1')
        product2 = Product.objects.get(name='Бургер2')

        data = {
            "products": [
                {"produkt": product1.id, 
                "quantity": 1
                },
                {"product": product2.id, 
                "quantity": 3
                },                
                ], 
            "firstname":  "Vasya",
            "lastname": "Petrov",
            "address": "Дыбенко",
            "phonenumber": "+79311234567",
        }      
        error, error_status = validate_data_from_frontend(data)
        self.assertNotEqual(error, None)
        self.assertEqual(error_status, status.HTTP_406_NOT_ACCEPTABLE)


    def test_firstname_is_null(self):
        """
        firstname: Это поле не может быть пустым.
        """
        product1 = Product.objects.get(name='Бургер1')
        product2 = Product.objects.get(name='Бургер2')

        data = {
            "products": [
                {"product": product1.id, 
                "quantity": 1
                },
                {"product": product2.id, 
                "quantity": 3
                },                
                ], 
            "firstname":  None,
            "lastname": "Petrov",
            "address": "Дыбенко",
            "phonenumber": "+79311234567",
        }      
        error, error_status = validate_data_from_frontend(data)
        self.assertNotEqual(error, None)
        self.assertEqual(error_status, status.HTTP_417_EXPECTATION_FAILED)


    def test_firstname_is_list(self):
        """
        В поле firstname положили список.
        firstname: Not a valid string.
        """
        product1 = Product.objects.get(name='Бургер1')
        product2 = Product.objects.get(name='Бургер2')

        data = {
            "products": [
                {"product": product1.id, 
                "quantity": 1
                },
                {"product": product2.id, 
                "quantity": 3
                },                
                ], 
            "firstname":  ['fdfdf'],
            "lastname": "Petrov",
            "address": "Дыбенко",
            "phonenumber": "+79311234567",
        }      
        error, error_status = validate_data_from_frontend(data)
        self.assertNotEqual(error, None)
        self.assertEqual(error_status, status.HTTP_406_NOT_ACCEPTABLE)



    def test_key_fields_lack(self):
        """
        Ключей заказа вообще нет.
        firstname, lastname, phonenumber, address: Обязательное поле.
        """
        product1 = Product.objects.get(name='Бургер1')
        product2 = Product.objects.get(name='Бургер2')

        data = {
            "products": [
                {"product": product1.id, 
                "quantity": 1
                },
                {"product": product2.id, 
                "quantity": 3
                },                
                ], 
        }      
        error, error_status = validate_data_from_frontend(data)
        self.assertNotEqual(error, None)
        self.assertEqual(error_status, status.HTTP_417_EXPECTATION_FAILED)


    def test_key_fields_are_null(self):
        """
        Ключи есть, но все со значением null.
        firstname, lastname, phonenumber, address: Это поле не может быть пустым.
        """
        product1 = Product.objects.get(name='Бургер1')
        product2 = Product.objects.get(name='Бургер2')

        data = {
            "products": [
                {"product": product1.id, 
                "quantity": 1
                },
                {"product": product2.id, 
                "quantity": 3
                },                
                ], 
            "firstname":  None,
            "lastname": None,
            "address": None,
            "phonenumber": None, 
        }      
        error, error_status = validate_data_from_frontend(data)
        self.assertNotEqual(error, None)
        self.assertEqual(error_status, status.HTTP_417_EXPECTATION_FAILED)  


    def test_phonenumber_is_empty(self):
        """
        Не указан номер телефона.
        phonenumber: Это поле не может быть пустым.
        """
        product1 = Product.objects.get(name='Бургер1')
        product2 = Product.objects.get(name='Бургер2')

        data = {
            "products": [
                {"product": product1.id, 
                "quantity": 1
                },
                {"product": product2.id, 
                "quantity": 3
                },                
                ], 
            "firstname": "Vasya",
            "lastname": "Petrov",
            "address": "Дыбенко",
            "phonenumber": "",                
        }      
        error, error_status = validate_data_from_frontend(data)
        self.assertNotEqual(error, None)
        self.assertEqual(error_status, status.HTTP_417_EXPECTATION_FAILED)


    def test_phonenumber_is_invalid(self):
        """
        Несуществующий номер телефона.
        phonenumber': Введен некорректный номер телефона.
        """
        product1 = Product.objects.get(name='Бургер1')
        product2 = Product.objects.get(name='Бургер2')

        data = {
            "products": [
                {"product": product1.id, 
                "quantity": 1
                },
                {"product": product2.id, 
                "quantity": 3
                },                
                ], 
            "firstname": "Vasya",
            "lastname": "Petrov",
            "address": "Дыбенко",
            "phonenumber": "+70000000000",                
        }      
        error, error_status = validate_data_from_frontend(data)
        self.assertNotEqual(error, None)
        self.assertEqual(error_status, status.HTTP_406_NOT_ACCEPTABLE)


