# auctions/management/commands/add_categories.py
from django.core.management.base import BaseCommand
from auctions.models import Category

class Command(BaseCommand):
    help = 'Add eBay categories to the database'

    def handle(self, *args, **kwargs):
        categories = [
            "Antiques",
            "Art",
            "Baby",
            "Books",
            "Business & Industrial",
            "Cameras & Photo",
            "Cell Phones & Accessories",
            "Clothing, Shoes & Accessories",
            "Coins & Paper Money",
            "Collectibles",
            "Computers/Tablets & Networking",
            "Consumer Electronics",
            "Crafts",
            "Drones & Multirotors",
            "Electronics",
            "Entertainment Memorabilia",
            "Gift Cards & Coupons",
            "Health & Beauty",
            "Home & Garden",
            "Jewelry & Watches",
            "Music",
            "Pet Supplies",
            "Pottery & Glass",
            "Real Estate",
            "Sporting Goods",
            "Sports Mem, Cards & Fan Shop",
            "Stamps",
            "Tickets & Experiences",
            "Toys & Hobbies",
            "Travel",
            "Video Games & Consoles",
        ]

        for category_name in categories:
            category, created = Category.objects.get_or_create(name=category_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully added category: {category_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Category already exists: {category_name}'))
