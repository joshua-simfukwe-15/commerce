from django.contrib import admin
from .models import AuctionListing, Bid, Comment, Category

class AuctionListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'current_price', 'active', 'created_at')
    list_filter = ('active',)
    search_fields = ('title', 'description')

    
class BidAdmin(admin.ModelAdmin):
    list_display = ('user', 'listing', 'amount', 'bid_time')
    list_filter = ('listing',)
    search_fields = ('user__username', 'listing__title')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'listing', 'content', 'created_at')
    list_filter = ('listing',)
    search_fields = ('user__username', 'listing__title')

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

# Register your models here.
admin.site.register(AuctionListing, AuctionListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Category, CategoryAdmin)
