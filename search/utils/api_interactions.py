#! /usr/bin/env python3
# coding: utf-8

import re
import random
import requests

class OpenFoodFactsInteractions:
    """
    This class groups all the methods to interact with the Openfoodfacts API
    """
    
    def get_products_selection(self, query, max_numb):
        """
        This method coordinates several methods from the class to give some example :
            -> If api sends back products, it cleaned them
            -> If selected product > wanted number, a process of selection is realized
            -> It returns the necessary dict at the end
        """

        data_from_api = self._get_products_from_api_search('brands', query, 150)
        if data_from_api["count"] <= 0:
            data_from_api = self._get_products_from_api_large_search(query, 150)

        if data_from_api["count"] > 0:
            products_selected = self._select_appropriate_products(data_from_api, query)
            if products_selected["number"] > max_numb :
                self._select_by_product_name(products_selected, max_numb)
                self._select_by_nutriscore_value(products_selected, max_numb)
                self._select_by_image(products_selected, max_numb)
                self._select_by_description(products_selected, max_numb)
                self._select_by_random_way(products_selected, max_numb)
            return products_selected
        else:
            return None



    def get_substitute_products_from_api(self, element_type, info_id, max_numb):
        """
        This method coordinates all 
        """
        if element_type == "category":
            data_from_api = self._get_products_from_api_search('categories', info_id, 1000)
        elif element_type == "product":
            # Maybe to optimize
            product = self._get_product_from_api_code_search(info_id)
            # we select the appropriate category
            product_categories = product["product"]["categories_hierarchy"]
            data_from_api = {}
            validated = False

            # We try to find an associated category to the product where there are at least 6 "a" products
            while not validated and len(product_categories) > 0:
                category_to_check = product_categories.pop()
                check_category = self._get_products_from_api_search('categories', category_to_check, 1000)
                substitute_product = 0
                for product in check_category["products"]:
                    try:
                        if product["nutrition_grade_fr"] == "a":
                            substitute_product += 1
                    except:
                        pass 
                if substitute_product >= max_numb:
                    validated = True
                    data_from_api = check_category

            # If we don't find any categories, we set up count attribute to 0
            if not validated:
                data_from_api["count"] = 0

        if data_from_api["count"] > 0:
            products_selected = self._select_substitute_products(data_from_api)
            if products_selected["number"] > max_numb :
                self._select_by_product_name(products_selected, max_numb)
                self._select_by_nutriscore_value(products_selected, max_numb)
                self._select_by_image(products_selected, max_numb)
                self._select_by_description(products_selected, max_numb)
                self._select_by_random_way(products_selected, max_numb)
            return products_selected
        else:
            return None          
    
    def get_selected_product(self, code):

        product_data = self._get_product_from_api_code_search(code)
        if product_data["status_verbose"] == "product found":
            product = self._select_product_info(product_data)
        else:
            product = None

        return product

    def _get_products_from_api_search(self, query_type, query, page_size):
        """
        This method gets all the products from the API linked to the brands asked by the user (query)
        """

        payload = {
            'action' : 'process',
            'json' : '1',
            'tagtype_0' : query_type,
            'tag_contains_0' : 'contains',
            'tag_0' : query,
            'page_size' : page_size,
            'page' : '1'
        }

        request = requests.get('https://fr.openfoodfacts.org/cgi/search.pl', params=payload)
        data = request.json()

        return data

    def _get_products_from_api_large_search(self, query, page_size):
        """
        This method gets all the products from the API linked to a query asked by the user (query)
        This is a arge request (more than the others), so the precisions in the results will be
        larger but less precise.
        """        
        payload = {
            'action' : 'process',
            'search_simple' : '1',
            'search_terms' : query,
            'page_size' : page_size,
            'page' : '1',
            'json' : '1'
        }
        request = requests.get('https://fr.openfoodfacts.org/cgi/search.pl', params=payload)
        data = request.json()

        return data

    def _get_product_from_api_code_search(self, code):

        request = requests.get("https://fr.openfoodfacts.org/api/v0/product/" + code + ".json")
        data = request.json()

        return data

    def _select_product_info(self, data):
        
        product_info = {
            "name" : "",
            "ref" : "",
            "description": "",
            "nutriscore": "",
            "image_url": "",
            "categories": [],
            "ingredients": "",
            "nutriments": {
                "fat": 0,
                "saturated_fat": 0,
                "sugar": 0,
                "salt": 0
            },
            "ingredients_image_url": "",
            "nutriments_image_url": "",
        }

        product_data = data["product"]

        product_info["name"] = product_data["product_name_fr"]
        product_info["ref"] = product_data["code"]
        product_info["nutriscore"] = product_data["nutrition_grade_fr"]
        
        try:
            if product_data["generic_name_fr"].strip():
                product_info["description"] = product_data["generic_name_fr"]
            else:
                product_info["description"] = "Information manquante"        
        except:
            product_info["description"] = "Information manquante"

        try:
            if product_data["image_url"].strip():
                product_info["image_url"] = product_data["image_url"]
            else:
                product_info["image_url"] = "Image manquante"
        except:
            product_info["image_url"] = "Image manquante"

        try:
            if len(product_data["categories_hierarchy"]) > 0:
                product_info["categories"] = product_data["categories_hierarchy"]
            else:
                product_info["categories"] = ["Information manquante"]                
        except:
            product_info["categories"] = ["Information manquante"]

        try:
            if product_data["ingredients_text_fr"].strip():
                product_info["ingredients"] = product_data["ingredients_text_fr"]
            else:
                product_info["ingredients"] = "Information manquante"                   
        except:
            product_info["ingredients"] = "Information manquante"   

        try:
            product_info["nutriments"]["fat"] = product_data["nutriments"]["fat_100g"]
        except:
            product_info["nutriments"]["fat"] = -1

        try:
            product_info["nutriments"]["saturated_fat"] = product_data["nutriments"]["saturated-fat_100g"]
        except:
            product_info["nutriments"]["saturated_fat"] = -1 

        try:
            product_info["nutriments"]["sugar"] = product_data["nutriments"]["sugars_100g"]
        except:
            product_info["nutriments"]["sugar"] = -1
        
        try:
            product_info["nutriments"]["salt"] = product_data["nutriments"]["salt_100g"]
        except:
            product_info["nutriments"]["salt"] = -1 

        try:
            if product_data["image_ingredients_url"].strip():
                product_info["ingredients_image_url"] = product_data["image_ingredients_url"]
            else:
                product_info["ingredients_image_url"] = "Image manquante"                
        except:
            product_info["ingredients_image_url"] = "Image manquante" 

        try:
            if product_data["image_nutrition_url"].strip():
                product_info["nutriments_image_url"] = product_data["image_nutrition_url"]
            else:
                product_info["nutriments_image_url"] = "Image manquante"                 
        except:
            product_info["nutriments_image_url"] = "Image manquante" 

        return product_info

    def _select_substitute_products(self, data):
        """
        This method gets the data from the API (products json linked to a category)
        and cleaned them to return only products:
            -> with a product name
            -> a nutriscore equal to "a"
            -> an image url
            -> a description
        """
        products_info = {
            'type' : 'product',
            'number' : 0,
            'elements': []
        }
        for product in data["products"]:
            element = {
                "name" : "",
                "ref" : "",
                "nutriscore" : "",
                "description" : "",
                "image_url" : "" 
            }
            try:
                if str(product["product_name_fr"]).split() and product["nutrition_grade_fr"] == "a":
                    element["name"] = product["product_name_fr"]
                    element["ref"] = product["code"]
                    element["nutriscore"] = product["nutrition_grade_fr"]
                    try:
                        element["description"] = product["generic_name_fr"]
                        element["image_url"] = product["image_url"]
                    except:
                        pass

                    products_info["elements"].append(element)
            except:
                pass

        products_info["number"] = len(products_info["elements"])

        return products_info

    def _select_appropriate_products(self, data, query):
        """
        This method gets the data from API and cleaned them to return only
        products
            -> where the query matchs with the product name
            -> with a nutriscore 
        """
        products_info = {
            'type' : 'product',
            'number' : 0,
            'elements': []
        }
        test = re.compile(r".*%s.*" % query, re.IGNORECASE)
        for product in data["products"]:
            try:
                at_least_one_category = product["categories_hierarchy"][0]
                appropriate_name = test.match(product["product_name_fr"])
                nutriscore = product["nutrition_grade_fr"]
            
                if appropriate_name and nutriscore and at_least_one_category:
                    element = {
                        "name" : "",
                        "ref" : "",
                        "nutriscore" : "",
                        "description" : "",
                        "image_url" : "" 
                    }
                    element["name"] = product["product_name_fr"]
                    element["nutriscore"] = nutriscore
                    element["ref"] = product["code"]
                    try:
                        element["description"] = product["generic_name_fr"]
                        element["image_url"] = product["image_url"]
                    except:
                        pass
            
                    products_info["elements"].append(element)
            except:
                pass

        products_info["number"] = len(products_info["elements"])

        return products_info

    def _select_by_image(self, data, max_numb):
        """
        This method removes products without image url from products list
        if the number of products is > max_numb
        """
        elements_cleaned = []
        products_numb = data["number"]
        for product in data["elements"]:
            if not product["image_url"] and products_numb > max_numb:
                products_numb -= 1
            else:
                elements_cleaned.append(product)
        data["elements"] = elements_cleaned
        data["number"] = products_numb
        return data

    def _select_by_description(self, data, max_numb):
        """
        This method removes products without description from products list
        if the number of products is > max_numb
        """
        elements_cleaned = []
        products_numb = data["number"]
        for product in data["elements"]:
            if not product["description"] and products_numb > max_numb:
                products_numb -= 1
            else:
                elements_cleaned.append(product)
        data["elements"] = elements_cleaned
        data["number"] = products_numb
        return data

    def _select_by_nutriscore_value(self, data, max_numb):
        """
        This method removes products with good nutriscore from products list
        if the number of products is > max_numb
        """
        elements_cleaned = []
        products_numb = data["number"]
        for product in data["elements"]:
            if product["nutriscore"] == "a" and products_numb > max_numb:
                products_numb -= 1
            else:
                elements_cleaned.append(product)
        data["elements"] = elements_cleaned
        data["number"] = products_numb
        return data

    def _select_by_random_way(self, data, max_numb):
        """
        This method selects on random way several products defines by max_numb
        argument if the length of the products is > max_numb 
        """
        if len(data["elements"]) > max_numb:
            random_product = random.sample(data["elements"], max_numb)
            data["elements"] = random_product

        data["number"] = len(data["elements"])

        return data

    def _select_by_product_name(self, data, max_numb):
        """
        This method removes products if a similar product name had already been accepted
        """
        elements_cleaned = []
        products_name_accepted = []
        products_numb = data["number"]
        for product in data["elements"]:
            if product["name"].lower() in products_name_accepted and products_numb > max_numb:
                products_numb -= 1
            else:
                elements_cleaned.append(product)
                products_name_accepted.append(product["name"].lower())

        data["elements"] = elements_cleaned
        data["number"] = products_numb
        return data
