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
        form = AuctionListingForm(request.POST)
        try:
            if form.is_valid():
                listing = form.save(commit=False)
                listing.seller = request.user
                listing.save()

                messages.success(request, "Your listing was successfully created!")
                return HttpResponseRedirect(reverse('index'))
            else:
                messages.error(request, "There was an error with your form. Please correct the errors and try again.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")             
    else:
        form = AuctionListingForm()
    
    return render(request, "auctions/create_listing.html", {
        "form": form
    })

def listing(request, listing_id):
    listing = get_object_or_404(AuctionListing, id=listing_id)
    user = request.user
    is_owner = listing.seller == user
    on_watchlist = False
    error_message =""

    if user.is_authenticated:
        on_watchlist = listing.watchers.filter(id=user.id).exists()

        if request.method == "POST":
            if "add_watchlist" in request.POST:
                listing.watchers.add(user)
            elif "remove_watchlist" in request.POST:
                listing.watchers.remove(user)
            elif "place_bid" in request.POST:
                amount = Decimal(request.POST["bid_amount"])
                if amount <= listing.current_price():
                    error_message = "Bid must be higher than the current price."
                else:
                    bid = Bid(user=user, listing=listing, amount=amount)
                    bid.save()
                    listing.current_price = amount
                    listing.save()  
            elif "close_auction" in request.POST:
                listing.active = False
                if listing.bid_set.exists():  # There are bids
                    highest_bid = listing.bid_set.order_by("-amount").first()
                    listing.winner = highest_bid.bidder
                listing.save()

            elif "post_comment" in request.POST:
                comment_content = request.POST["comment"]
                comment = Comment(user=user, listing=listing, content=comment_content)
                comment.save()

    context = {
        "listing": listing,
        "is_owner": is_owner,
        "on_watchlist": on_watchlist,
        "comments": listing.comments.all(),
        "error_message": error_message,

    }

    return render(request, "auctions/listing.html", context)