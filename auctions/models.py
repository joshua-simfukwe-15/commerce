from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)

    class Meta:
        verbose_name = "Category"  
        verbose_name_plural = "Categories"  

    def __str__(self):
        return self.name
    
# Model for auction listing
class AuctionListing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="listings")
    created_at = models.DateTimeField(auto_now_add=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='listing_images/', null=True, blank=True)  # Ensure this is included
    watchers = models.ManyToManyField(User, blank=True, related_name="watchlist")

    def current_price(self):
        bids = self.bids.all()

        if bids.exists():
            return bids.order_by('-amount').first().amount
        
        else:
            return self.starting_bid

    def __str__(self):
        return self.title

# Model for bids
class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    bid_time = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Ensure that the bid amount is higher than the current price
        if self.listing.current_price() is not None and self.amount <= self.listing.current_price():
            raise ValidationError(f"Your bid must be higher than the current price of {self.listing.current_price}.")

    def save(self, *args, **kwargs):
        # Call clean to validate the bid before saving
        self.clean()
        # Update the current price of the listing
        self.listing.current_price = self.amount
        self.listing.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} bid {self.amount} on {self.listing.title}"

# Model for comments
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.listing.title}"
