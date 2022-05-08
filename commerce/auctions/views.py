from django.utils import timezone
from datetime import date
from cProfile import label
from tkinter.tix import Select
from unicodedata import category
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms


from .models import ListingCategory, Listing, WatchListing, Comment
from .models import User


class CreateForm(forms.Form):
    title = forms.CharField(label="Title", max_length=100,widget=forms.TextInput(attrs={'class': 'form-control'}) )
    description = forms.CharField(label="Description", max_length=500,widget=forms.TextInput(attrs={'class': 'form-control'}))
    category = forms.ModelChoiceField(queryset=ListingCategory.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    starting_price = forms.DecimalField(label="Starting Price", max_digits=6, decimal_places=2, min_value=0.5,widget=forms.NumberInput(attrs={'class': 'form-control'}))
    image_url = forms.URLField(label="Image URL", required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))
    expiry_date = forms.DateField(label="Expiry Date",widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'min': date.today().strftime('%Y-%m-%d')}))

def index(request):
    # listings that have an expiration date of today or later
    active_listings = Listing.objects.filter(expires_at__gte=date.today())
    return render(request, "auctions/index.html", {
    "active_listings":active_listings
    })

def watch_list_add_remove(request, listing_id):
    if "watchlist_remove" in request.POST:
        WatchListing.objects.filter(user=request.user, listing=listing_id).delete()
    elif "watchlist_add" in request.POST:
        WatchListing.objects.create(user=request.user, listing=listing_id)

def add_bid(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    if listing.current_price < float(request.POST["bid"]):
        listing.current_price = float(request.POST["bid"])
        listing.save()

def add_comment(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    comment = Comment(text=request.POST["comment"], listing=listing, user=request.user)
    comment.save()

def listing(request, listing_id):
    # if the listing is not valid, go directly to home page
    if not Listing.objects.get(pk=listing_id):
        return HttpResponseRedirect(reverse("index"))
    # if the request is post and the user is authenticated
    # watchlist
    seller = Listing.objects.get(pk=listing_id).seller
    if request.method == "POST" and request.user.is_authenticated:
        if "watchlist" in request.POST:
            watch_list_add_remove(request, listing_id)
    # bid if the user is not the seller
        elif "bid" in request.POST and request.user != seller:
            add_bid(request, listing_id)
    # close bid 
        elif "close_bid" in request.POST and request.user == seller:
            # set the listing to sold
            listing = Listing.objects.get(pk=listing_id)
            listing.sold = True
            listing.save()
    # comment
        elif "comment" in request.POST:
            add_comment(request, listing_id)
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
            
    # Request is get
    # get the listing from the database
    else:
        listing = Listing.objects.get(pk=listing_id)
        # check if active listing
        active = listing.expires_at < timezone.now() 
        # check if sold or not 
        sold = listing.sold
        # watchlist if user is logged in
        watchlist = None
        if request.user.is_authenticated:
            watchlist = WatchListing.objects.filter(user=request.user, listing=listing)
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "active": active,
            "sold": sold,
            "bidder": listing.highest_bidder or None,
            "watchlist": watchlist
        })
    
    
def create(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))
    if request.method != "POST":
        return render(request, "auctions/create.html",{
         "category_list": ListingCategory.objects.all(), 
         "form": CreateForm()
        })
    # Validating date here 
    form = CreateForm(request.POST)
    if form.is_valid():
    # Form processing
        image_url = form.cleaned_data["image_url"] or None
        listing = Listing(title=form.cleaned_data["title"], description=form.cleaned_data["description"], 
                            category=form.cleaned_data["category"], starting_bid=form.cleaned_data["starting_price"], image_url=image_url, 
                            expires_at=form.cleaned_data["expiry_date"], seller=request.user, current_price = form.cleaned_data["starting_price"])
        listing.save()
    # Redirect to index
    return HttpResponseRedirect(reverse("index"))

def login_view(request):
    if request.method != "POST":
        return render(request, "auctions/login.html")
    # Attempt to sign user in
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)

    if user is None:
        return render(request, "auctions/login.html", {
            "message": "Invalid username and/or password."
        })
    login(request, user)
    return HttpResponseRedirect(reverse("index"))


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method != "POST":
        return render(request, "auctions/register.html")
    username = request.POST["username"]
    email = request.POST["email"]

    # Ensure password matches confirmation
    password = request.POST["password"]
    confirmation = request.POST["confirmation"]
    if password != confirmation:
        return render(request, "auctions/register.html", {
            "message": "Passwords must match."
        })

    # Attempt to create new user
    try:
        user = User.objects.create_user(username, email, password)
        user.save()
    except IntegrityError:
        return render(request, "auctions/register.html", {
            "message": "Username already taken."
        })
    login(request, user)
    return HttpResponseRedirect(reverse("index"))

def watchlist(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))
    if request.method != "POST":
        watchlist = WatchListing.objects.filter(user=request.user)
        return render(request, "auctions/watchlist.html", {
            "watchlist": watchlist
        })
    
    
    