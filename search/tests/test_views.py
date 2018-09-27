#! /usr/bin/env python3
# coding: utf-8
from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from django.core import mail
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from ..views import index, choice
from ..utils.treatment import Treatment
from ..models import Product, Category, Profile

class IndexPageTestCase(TestCase):
    """
    This class tests the index page view
    """

    def test_index_page_status(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

class ChoicePageTestCase(TestCase):
    """
    This class tests the choice page view
    """

    @patch('search.utils.treatment.Treatment.get_choice_selection')
    def test_choice_page_success(self, mock_get_choice_selection):
        """
        This method tests if there is a status 200 if a query is present in the url
        """

        mock_get_choice_selection.return_value = {
            'type' : 'product',
            'number' : 6,
            'elements' : [
                {
                    "name" : "Nutella",
                    "ref": "3017620429484",
                    "nutriscore": "e",
                    "description": "Pâtes à tartiner aux noisettes et au cacao",
                    "image_url": "https://static.openfoodfacts.org/images/products/301/762/404/7813/front_fr.42.400.jpg",
                },
                {
                    "name" : "Pâte à Tartiner Nutella,",
                    "ref": "364561612564",
                    "nutriscore": "e",
                    "description": "Pâtes à tartiner aux noisettes et au cacao",
                    "image_url": "https://static.openfoodfacts.org/images/products/301/762/404/7813/front_fr.42.400.jpg",
                },
                {
                    "name" : "Pate Tartiner Nutella 750G",
                    "ref": "54651861",
                    "nutriscore": "e",
                    "description": "Pâtes à tartiner aux noisettes et au cacao",
                    "image_url": "https://static.openfoodfacts.org/images/products/301/762/404/7813/front_fr.42.400.jpg",
                },
                {
                    "name" : "Biscuits B Ready noisettes/cacao Nutella",
                    "ref": "3453548914",
                    "nutriscore": "e",
                    "description": "",
                    "image_url": "https://static.openfoodfacts.org/images/products/301/762/404/7813/front_fr.42.400.jpg",
                }, 
                {
                    "name" : "Nutella au caramel",
                    "ref": "301776542",
                    "nutriscore": "b",
                    "description": "Pâtes à tartiner aux noisettes et au caramel",
                    "image_url": "https://static.openfoodfacts.org/images/products/301/762/404/7813/front_fr.42.400.jpg",
                },
                {
                    "name" : "gateaux Nutella et caramel,",
                    "ref": "364561614754",
                    "nutriscore": "b",
                    "description": "Pâtes à tartiner aux noisettes et au cacao",
                    "image_url": "https://static.openfoodfacts.org/images/products/301/762/404/7813/front_fr.42.400.jpg",
                },
            ] 
        }

        data = {
            'search': 'nutella'
        }

        response = self.client.get(reverse('search:choice'), data)
        self.assertEqual(response.status_code, 200)

    def test_choice_page_fail(self):
        """
        This method tests if a 404 status is raised if there is not query in the url
        (or a simple space)
        """

        data = {
            'search': ' '
        }
        response = self.client.get(reverse('search:choice'), data)
        self.assertEqual(response.status_code, 404)

class ProductPageTestCase(TestCase):
    """
    This class tests the product page view
    """
    @classmethod
    def setUpTestData(cls):

        # We add two products
        products = [
            {
                "product_name_fr": "Le jus de raisin 100% jus de fruits",
                "code": "123456789",
                "image_url":"https://static.openfoodfacts.org/images/products/609/109/100/0301/front_fr.13.100.jpg",
                "nutrition_grade_fr": "a",
                "generic_name_fr" : "jus de fruit naturel sans sucre ajouté",
                "categories_hierarchy": [
                    "en:plant-based-foods-and-beverages",
                    "en:beverages",
                ],
            },
            {
                "product_name_fr": "Le haricot 100% naturellement bleue",
                "code": "987654321",
                "image_url": "https://static.openfoodfacts.org/images/products/152/haricot.jpg",
                "nutrition_grade_fr": "b",
                "generic_name_fr" : "",
                "categories_hierarchy": [
                    "en:plant-based-foods",
                ],
            },
        ]
        for product in products:
            new_product = Product.objects.create(name=product["product_name_fr"].lower(),
                                   ref=product["code"],
                                   nutriscore=product["nutrition_grade_fr"],
                                   picture=product["image_url"],
                                   description=product["generic_name_fr"])
            
            for category in product["categories_hierarchy"]:
                try:
                    cat_in_db = Category.objects.get(api_id=category) 
                    new_product.categories.add(cat_in_db)
                except:
                    pass

        # We add a user who registered the "Le jus de raisin 100% jus de fruits" product
        username = 'test-ref'
        mail = 'test-ref@register.com'
        password = 'ref-test-view'
        password_check = 'ref-test-view'
        user = User.objects.create_user(username, mail, password)
        user_profile = Profile(user=user)
        user_profile.save()
        product = Product.objects.get(ref="123456789")
        user_profile.products.add(product.id)

    @patch('search.utils.treatment.Treatment.get_selected_product')
    def test_product_page_get(self, mock_get_selected_product):
        """
        This method tests if there is a 200 status when a product is returned from the api
        """

        mock_get_selected_product.return_value = {
            "name" : "Le jus de raisin 100% jus de fruits",
            "ref" : "123456789",
            "description": "jus de fruit naturel sans sucre ajouté",
            "nutriscore": "a",
            "image_url": "https://static.openfoodfacts.org/images/products/609/109/100/0301/front_fr.13.100.jpg",
            "categories": [
                "en:plant-based-foods-and-beverages",
                "en:beverages",
            ],
            "ingredients": "du jus et du fruit (principalement du raisin)",
            "nutriments": {
                "fat": 0.2,
                "saturated_fat": 0,
                "sugar": 10,
                "salt": 0
            },
            "ingredients_image_url": "https://static.openfoodfacts.org/images/products/609/109/100/0301/front_fr.13.100.jpg",
            "nutriments_image_url": "https://static.openfoodfacts.org/images/products/609/109/100/0301/front_fr.13.100.jpg",
        }

        code = Product.objects.get(ref="123456789").ref
        response = self.client.get(reverse('search:product', args=(code,)))
        self.assertEqual(response.status_code, 200)

    @patch('search.utils.treatment.Treatment.get_selected_product')
    def test_product_page_user_product_registered(self, mock_get_selected_product):
        """
        This method mainly tests if the 'product_registered' variable returns True
        when the user is authenticated and he already resgitered the product returned by the API
        """

        mock_get_selected_product.return_value = {
            "name" : "Le jus de raisin 100% jus de fruits",
            "ref" : "123456789",
            "description": "jus de fruit naturel sans sucre ajouté",
            "nutriscore": "a",
            "image_url": "https://static.openfoodfacts.org/images/products/609/109/100/0301/front_fr.13.100.jpg",
            "categories": [
                "en:plant-based-foods-and-beverages",
                "en:beverages",
            ],
            "ingredients": "du jus et du fruit (principalement du raisin)",
            "nutriments": {
                "fat": 0.2,
                "saturated_fat": 0,
                "sugar": 10,
                "salt": 0
            },
            "ingredients_image_url": "https://static.openfoodfacts.org/images/products/609/109/100/0301/front_fr.13.100.jpg",
            "nutriments_image_url": "https://static.openfoodfacts.org/images/products/609/109/100/0301/front_fr.13.100.jpg",
        }

        user = self.client.login(username='test-ref', password='ref-test-view')
        
        user = User.objects.get(username='test-ref')
        code = Product.objects.get(ref="123456789").ref

        response = self.client.get(reverse('search:product', args=(code,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['product_registered'], True)

    @patch('search.utils.treatment.Treatment.get_selected_product')
    def test_product_page_user_product_non_registered(self, mock_get_selected_product):
        """
        This method mainly tests if the 'product_registered' variable returns False
        when the user is authenticated but did not registered yet the product returned
        by the API
        """

        mock_get_selected_product.return_value = {
            "name" : "Le haricot 100% naturellement bleue",
            "ref" : "987654321",
            "description": "jus de fruit naturel sans sucre ajouté",
            "nutriscore": "b",
            "image_url": "https://static.openfoodfacts.org/images/products/152/haricot.jpg",
            "categories": [
                "en:plant-based-foods",
            ],
            "ingredients": "du haricot bleue mais 100% naturel.",
            "nutriments": {
                "fat": 0.6,
                "saturated_fat": 0.1,
                "sugar": 0,
                "salt": 2
            },
            "ingredients_image_url": "https://static.openfoodfacts.org/images/products/152/haricot.jpg",
            "nutriments_image_url": "https://static.openfoodfacts.org/images/products/152/haricot.jpg",
        }       

        user = self.client.login(username='test-ref', password='ref-test-view')
        
        user = User.objects.get(username='test-ref')
        code = Product.objects.get(ref="987654321").ref

        response = self.client.get(reverse('search:product', args=(code,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['product_registered'], False)

class RegisterPageTestCase(TestCase):
    """
    This class tests the register page view
    """
    
    @classmethod
    def setUpTestData(cls):
        username = 'test-ref'
        mail = 'test-ref@register.com'
        password = 'ref-test-view'
        password_check = 'ref-test-view'
        User.objects.create_user(username, mail, password)

    def test_register_page_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_register_page_success_registration(self):
        """
        The method tests the behavior of the app when a registration is done
        with good informations
        """

        data = {
            'username' : 'test-page',
            'mail' : 'test-unitaire@register.com',
            'password' : 'test-unitaire-view',
            'password_check' : 'test-unitaire-view',
        }

        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('log_in'))

    def test_register_page_fail_registration(self):
        """
        The methods tests the behavior of the app when a registration is done
        but with a username which already exists in the database
        """

        data = {
            'username' : 'test-ref',
            'mail' : 'test-unitaire@register.com',
            'password' : 'test-unitaire-view',
            'password_check' : 'test-unitaire-view',
        }

        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['error'], True)

class LoginPageTestCase(TestCase):
    """
    This class tests the log-in page view
    """

    @classmethod
    def setUpTestData(cls):
        username = 'username-existing'
        mail = 'test-ref@register.com'
        password = 'existing-ref'
        password_check = 'existing-ref'
        User.objects.create_user(username, mail, password)

    def test_login_page_get(self):
        response = self.client.get(reverse('log_in'))
        self.assertEqual(response.status_code, 200)

    def test_login_page_success_connexion(self):
        """
        The method tests the behavior of the app when a connexion
        is correctly realized
        """

        data = {
            'username' : 'username-existing',
            'password' : 'existing-ref',
        }

        response = self.client.post(reverse('log_in'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('search:personal'))
    
    def test_login_page_fail_connexion_username(self):
        """
        The method tests the behavior of the app when there is a connexion attempt
        is done with a wrong username
        """

        data = {
            'username' : 'unknown',
            'password' : 'existing-ref',
        }

        response = self.client.post(reverse('log_in'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['error'], True)

    def test_login_page_fail_connexion_password(self):
        """
        The method tests the behavior of the app when there is a connexion attempt
        is done with a wrong password
        """

        data = {
            'username' : 'username-existing',
            'password' : 'unknown-ref',
        }

        response = self.client.post(reverse('log_in'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['error'], True)

class LogoutPageTestCase(TestCase):
    """
    This class tests the log-out page view
    """

    def test_logout_page(self):
        """
        The method tests the behavior of the app whn a log out is done
        """
        response = self.client.get(reverse('log_out'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('log_in'))

class PersonalPageTestCase(TestCase):
    """
    This class tests the personal account page view
    """

    @classmethod
    def setUpTestData(cls):
        username = 'username-existing'
        mail = 'test-ref@register.com'
        password = 'existing-ref'
        password_check = 'existing-ref'
        user = User.objects.create_user(username, mail, password)
        user_profile = Profile(user=user)
        user_profile.save()

    def test_personal_page_connected(self):
        """
        This method tests the behavior of the app when a connected user
        tries to access to the personal account page
        """
        user = self.client.login(username='username-existing', password='existing-ref')
        response = self.client.get(reverse('search:personal'))
        self.assertEqual(response.status_code, 200)

    def test_personal_page_non_connected(self):
        """
        This method tests the behavior of the app when a non-connected user
        tries to access to the personal account page
        """
        response = self.client.get(reverse('search:personal'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/search/personal-account')

class ProductRegisteredPageTestCase(TestCase):
    """
    This class tests the product-registered page view
    """
    
    @classmethod
    def setUpTestData(cls):
        username = 'username-existing'
        mail = 'test-ref@register.com'
        password = 'existing-ref'
        password_check = 'existing-ref'
        user = User.objects.create_user(username, mail, password)
        user_profile = Profile(user=user)
        user_profile.save()

    def test_product_registered_page_connected(self):
        """
        This method tests the behavior of the app when a connected user
        tries to access to the personal product registered page
        """
        user = self.client.login(username='username-existing', password='existing-ref')
        response = self.client.get(reverse('search:product_registered'))
        self.assertEqual(response.status_code, 200)

    def test_product_registered_page_non_connected(self):
        """
        This method tests the behavior of the app when a non-connected user
        tries to access to the personal product registered page
        """
        response = self.client.get(reverse('search:product_registered'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/search/product-registered')

class EmailTest(TestCase):

    def test_send_email(self):
        
        # Send message.
        mail.send_mail(
            'Subject of the mail', 'Message of the mail',
            'from@example.com', ['to@example.com'],
            fail_silently=False,
        )

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the subject of the first message is correct.
        self.assertEqual(mail.outbox[0].subject, 'Subject of the mail')
        self.assertEqual(mail.outbox[0].body, 'Message of the mail')