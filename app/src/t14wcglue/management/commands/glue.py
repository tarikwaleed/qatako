from django.core.management.base import BaseCommand
import logging
import inspect
import time
from shared.models import CommandException
from t14wcglue.utils import T14Manager
from pprint import pprint
from woocommerce import API
import os
import json

from core.settings import BASE_DIR


class Command(BaseCommand):
    def handle(self, *args, **options):
        exception_count = 0
        start_time = time.time()

        logger = logging.getLogger(__name__)
        exception_logger = logging.getLogger("exceptions")

        logger.info(
            "----------------------------------------------------------------------------------------------------------------------------------------------------"
        )

        current_function_name = inspect.currentframe().f_code.co_name
        try:

            manager = T14Manager()
            items = manager.get_all_items()

            with open(
                BASE_DIR.parent / "resources" / "t14" / "all_fitment.json", "w"
            ) as outfile:
                outfile.write(json.dumps(items))

            return
            products=[]
            if items:
                for item in items[:5]:
                    if item is None:
                        raise ValueError("Item is None")

                    attributes = item.get('attributes')
                    if attributes is None:
                        raise ValueError(f"Attributes are None for item ID: {item.get('id')}")

                    product_id = item.get('id')
                    product_name = attributes.get('product_name')
                    product_category = attributes.get('category')
                    product_subcategory = attributes.get('subcategory')

                    # Handle dimensions as a list of dictionaries
                    dimensions = attributes.get('dimensions')
                    if not dimensions or not isinstance(dimensions, list) or len(dimensions) == 0:
                        raise ValueError(f"Dimensions are None or not valid for item ID: {product_id}")

                    # Assuming you want to work with the first set of dimensions
                    dimension_data = dimensions[0]
                    weight = str(dimension_data.get('weight'))
                    length = str(dimension_data.get('length'))
                    width = str(dimension_data.get('width'))
                    height = str(dimension_data.get('height'))

                    brand = attributes.get('brand')
                    thumbnail = attributes.get('thumbnail')
                    barcode = attributes.get('barcode')

                    item_data = manager.get_single_item_data(item_id=product_id)
                    if item_data is None:
                        raise ValueError(f"Item data is None for item ID: {product_id}")

                    files = item_data.get('files')
                    images = []

                    if files:
                        for file in files:
                            file_type = file.get('type')
                            if file_type == 'Image'  :
                                links = file.get('links')
                                if links:
                                    images.append({
                                        "src": links[0].get('url')
                                    })


                    product_description = ""
                    product_short_description = ""
                    item_descriptions = item_data.get('descriptions')
                    if item_descriptions:
                        for description in item_descriptions:
                            description_type = description.get('type')
                            description_text = description.get('description', "")
                            if " - Short" in description_type:
                                product_short_description = description.get('description')
                            else :
                                if product_description:  # Check if it's not the first description
                                    product_description += "\n"  # Add a newline before adding new description
                                product_description += description_text
                    #
                    product_price = manager.get_single_item_price(item_id=product_id)
                    if product_price is None:
                        raise ValueError(f"Product price is None for item ID: {product_id}")


                    result = {}

                    if product_id is not None:
                        result["product_id"] = product_id
                    if product_name is not None:
                        result["product_name"] = product_name
                    if product_category is not None:
                        result["category"] = product_category
                    if product_subcategory is not None:
                        result["subcategory"] = product_subcategory
                    if weight is not None:
                        result["weight"] = weight
                    if length is not None:
                        result["length"] = length
                    if width is not None:
                        result["width"] = width
                    if height is not None:
                        result["height"] = height
                    if brand is not None:
                        result["brand"] = brand
                    if thumbnail is not None:
                        result["thumbnail"] = thumbnail
                    if barcode is not None:
                        result["barcode"] = barcode
                    if images:
                        result["images"] = images
                    if product_description:
                        result["product_description"] = product_description
                    if product_short_description:
                        result["product_short_description"] = product_short_description
                    if product_price is not None:
                        result["product_price"] = product_price
                    self.stdout.write(self.style.SUCCESS(f"تم سحب كافة بيانات المنتج رقم {product_id}"))

                    products.append(result)

            wcapi = API(
                url=os.getenv('WC_URL'),
                consumer_key=os.getenv('WC_CONSUMER_KEY'),
                consumer_secret=os.getenv('WC_CONSUMER_SECRET'),
                wp_api=True,
                version="wc/v3",
                timeout=100,
            )
            for product in products:

                data = {
                    "name": product.get('product_name'),
                    "type": "external",
                    "regular_price": product.get('product_price', "21.99"),  
                    "description": product.get('product_description', ""),
                    "short_description": product.get('product_short_description', ""),
                    "weight": str(product.get('weight', "")),  
                    "dimensions": {
                        "length": product.get('length', ""),
                        "width": product.get('width', ""),
                        "height": product.get('height', ""),
                    },
                    "images": product.get('images', []),  
                }
                wcapi.post("products", data).json()
                self.stdout.write(self.style.SUCCESS("تم اضافة المنتج بنجاح الى المتجر "))
        except Exception as e:
            exception_count += 1
            exception_logger.error(
                f"exception happened in Package:{__package__} Module:{__name__} Function:{current_function_name}(): {e}"
            )

        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"Synced in {duration:.2f} seconds")
        if exception_count > 0:
            self.stdout.write(
                self.style.ERROR(
                    f"Synced with {exception_count} exceptions in {duration:.2f} seconds"
                )
            )

            command_exception = CommandException(
                command=__name__, count=exception_count
            )
            command_exception.save()
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Synced without exception in {duration:.2f} seconds"
                )
            )
