from decimal import Decimal
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import User, AuctionListing, Bid, Comment
from .forms import AuctionListingForm

def index(request):
    active_listings = AuctionListing.objects.filter(active=True)

    return render(request, "auctions/index.html", {
        "active_listings": active_listings,
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
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
    else:
        return render(request, "auctions/register.html")

@login_required
def create_listing(request):
    if request.method == "POST":
        form = AuctionListingForm(request.POST, request.FILES)  # Make sure to include request.FILES
        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = request.user  # Set the seller to the current user
            listing.save()
            messages.success(request, "Listing created successfully!")
            return redirect('index')
        else:
            messages.error(request, "Error creating listing. Please check the form.")
    else:
        form = AuctionListingForm()

    return render(request, "auctions/create_listing.html", {"form": form})

def listing(request, listing_id):
    listing = get_object_or_404(AuctionListing, id=listing_id)
    user = request.user
    is_owner = listing.seller == user
    error_message =""

    if request.method == "POST":
        if "place_bid" in request.POST:
            amount = Decimal(request.POST["bid_amount"])
            if amount <= listing.current_price():
                error_message = "Bid must be higher than the current price."
            else:
                bid = Bid(user=user, listing=listing, amount=amount)
                bid.save()
                listing.current_price = amount
                listing.save()  
        if "close_auction" in request.POST:
            listing.active = False
            if listing.bid_set.exists():  # There are bids
                highest_bid = listing.bid_set.order_by("-amount").first()
                listing.winner = highest_bid.bidder
            listing.save()

        if "post_comment" in request.POST:
            comment_content = request.POST["comment"]
            comment = Comment(user=user, listing=listing, content=comment_content)
            comment.save()

    context = {
        "listing": listing,
        "is_owner": is_owner,
        "comments": listing.comments.all(),
        "error_message": error_message,

    }

    return render(request, "auctions/listing.html", context)

@login_required
def watchlist(request):
    user = request.user
    watchlist = user.watchlist.all()

    return render(request, "auctions/watchlist.html",{
        "watchlist": watchlist
    })

@login_required
def toggle_watchlist(request, listing_id):
    listing = get_object_or_404(AuctionListing, id=listing_id)

    if listing in request.user.watchlist.all():
        request.user.watchlist.remove(listing)
    else:
        request.user.watchlist.add(listing)
    return HttpResponseRedirect(reverse('listing', args=[listing.id]))



