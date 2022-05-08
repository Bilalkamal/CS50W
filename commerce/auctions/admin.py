from django.contrib import admin

from .models import ListingCategory, Listing, WatchListing

# Register your models here.
admin.site.register(ListingCategory)
admin.site.register(Listing)
admin.site.register(WatchListing)