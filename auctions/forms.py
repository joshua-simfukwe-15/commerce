from django import forms
from .models import AuctionListing

class AuctionListingForm(forms.ModelForm):
    class Meta:
        model = AuctionListing
        fields = ['title', 'description', 'starting_bid', 'image_url', 'category']
        widget = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'category': forms.Select(),
        }