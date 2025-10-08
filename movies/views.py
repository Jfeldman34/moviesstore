from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, RequestedMovie, Rating
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg

def index(request):
    search_term = request.GET.get('search')
    movies = Movie.objects.filter(name__icontains=search_term) if search_term else Movie.objects.all()

    template_data = {
        'title': 'Movies',
        'movies': movies,
        'top_reviews': Review.objects.order_by('-rating')[:5],
        'recent_reviews': Review.objects.order_by('-date')[:5],
        'pop_reviews': Review.objects.annotate(num_likes=Count('liked_users')).order_by('-num_likes')[:5],
        'top_movies': Movie.objects.annotate(times_ordered=Sum('item__quantity')).order_by('-times_ordered')[:3],
        'recent_movies': Movie.objects.order_by('-date')[:3],
        # Updated to use Rating model for average ratings
        'top_movies_by_rating': Movie.objects.annotate(avg_rating=Avg('rating__rating')).order_by('-avg_rating')[:3],
        'top_movies_by_likes': Movie.objects.annotate(num_likes=Count('liked_users')).order_by('-num_likes')[:3],
        'requested_movies': RequestedMovie.objects.all().order_by('-requested_at'),
    }

    if request.user.is_authenticated:
        # movies liked by this user
        template_data['liked_movies'] = (
            Movie.objects
            .filter(liked_users=request.user)
            .annotate(avg_rating=Avg('rating__rating'))
        )

        template_data['ordered_movies'] = (
            Movie.objects
            .filter(item__order__user=request.user)
            .annotate(total_ordered=Sum('item__quantity'))
            .annotate(avg_rating=Avg('rating__rating'))
            .order_by('-total_ordered')
        )
    else:
        template_data['liked_movies'] = Movie.objects.none()
        template_data['ordered_movies'] = Movie.objects.none()

    return render(request, 'movies/index.html', {'template_data': template_data})


def delete_request(request, request_id):
    if request.method == "POST":
        movie_request = get_object_or_404(RequestedMovie, id=request_id)
        movie_request.delete()
    return redirect('movies.index')


@login_required
def like_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if request.user in review.liked_users.all():
        # User already liked → unlike
        review.liked_users.remove(request.user)
    else:
        # User has not liked → like
        review.liked_users.add(request.user)

    return redirect('movies.show', id=review.movie.id)


def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie)
    top_review = reviews.order_by('-rating').first()
    
    # Get user's rating if they're logged in
    user_rating = None
    if request.user.is_authenticated:
        try:
            user_rating = Rating.objects.get(movie=movie, user=request.user)
        except Rating.DoesNotExist:
            user_rating = None
    
    # Calculate average rating from Rating model
    avg_rating = Rating.objects.filter(movie=movie).aggregate(Avg('rating'))['rating__avg']
    
    template_data = {
        'title': movie.name,
        'movie': movie,
        'reviews': reviews,
        'top_review': top_review,
        'user_rating': user_rating,
        'avg_rating': avg_rating,
    }
    return render(request, 'movies/show.html', {'template_data': template_data})


@login_required
def like_movie(request, id):
    movie = get_object_or_404(Movie, id=id)
    if request.user in movie.liked_users.all():
        movie.liked_users.remove(request.user)
    else:
        movie.liked_users.add(request.user)
    movie.save()
    return redirect('movies.show', id=id)


@login_required
def rate_movie(request, id):
    """Rate a movie without writing a review"""
    if request.method == 'POST':
        movie = get_object_or_404(Movie, id=id)
        rating_value = request.POST.get('rating')
        
        if rating_value:
            rating_value = int(rating_value)
            if 1 <= rating_value <= 10:
                # Update or create rating
                rating, created = Rating.objects.update_or_create(
                    movie=movie,
                    user=request.user,
                    defaults={'rating': rating_value}
                )
    
    return redirect('movies.show', id=id)


@login_required
def delete_rating(request, id):
    """Delete user's rating for a movie"""
    if request.method == 'POST':
        movie = get_object_or_404(Movie, id=id)
        try:
            rating = Rating.objects.get(movie=movie, user=request.user)
            rating.delete()
        except Rating.DoesNotExist:
            pass
    
    return redirect('movies.show', id=id)


@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)


@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)


@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    
    if request.method == 'GET':
        template_data = {
            'title': 'Edit Review',
            'review': review
        }
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    
    elif request.method == 'POST' and request.POST['comment'] != '':
        review.comment = request.POST['comment']
        rating = request.POST.get('rating')
        if rating:
            review.rating = int(rating)
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)


def request_movie(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        if title and description:
            RequestedMovie.objects.create(
                title=title.strip(),
                description=description.strip(),
                requested_by=request.user if request.user.is_authenticated else None
            )
    return redirect('movies.index')


# Add these to your existing movies/views.py
from django.http import JsonResponse
from django.db.models import Count, Sum
from cart.models import Item
from accounts.models import UserProfile
from django.shortcuts import render

def popularity_map(request):
    """Display the geographic popularity map"""
    template_data = {
        'title': 'Global Popularity Map',
    }
    return render(request, 'movies/popularity_map.html', {'template_data': template_data})


def map_data(request):
    """API endpoint to get trending movies by country"""
    region = request.GET.get('region', None)
    
    countries_data = {}
    
    # Query to get top movies by country based on purchases
    items = Item.objects.select_related('order__user__profile', 'movie').all()
    
    for item in items:
        profile = item.order.user.profile
        # Get country name from django-countries CountryField
        country = profile.country.name if profile.country else 'Unknown'
        
        if country == 'Unknown' or not country:
            continue
        
        if country not in countries_data:
            countries_data[country] = {}
        
        movie_name = item.movie.name
        if movie_name not in countries_data[country]:
            countries_data[country][movie_name] = {
                'count': 0,
                'movie_id': item.movie.id,
                'price': item.movie.price
            }
        
        countries_data[country][movie_name]['count'] += item.quantity
    
    # Format data for frontend
    regions = []
    for country, movies in countries_data.items():
        # Sort movies by count
        sorted_movies = sorted(movies.items(), key=lambda x: x[1]['count'], reverse=True)
        top_movies = []
        
        for movie_name, data in sorted_movies[:10]:  # Top 10 movies
            top_movies.append({
                'name': movie_name,
                'count': data['count'],
                'id': data['movie_id']
            })
        
        regions.append({
            'region': country,
            'top_movies': top_movies,
            'total_purchases': sum(m[1]['count'] for m in sorted_movies)
        })
    
    # If specific region requested, return just that region
    if region:
        region_data = next((r for r in regions if r['region'] == region), None)
        if region_data:
            return JsonResponse(region_data)
        return JsonResponse({'error': 'Region not found'}, status=404)
    
    # Return all regions
    return JsonResponse({'regions': regions})


def trending_by_region(request, region):
    """View trending movies for a specific country"""
    # django-countries stores 2-letter country codes, but we're using names in the URL
    # We need to get items where the country name matches
    from django_countries import countries
    
    # Find country code from name
    country_code = None
    for code, name in countries:
        if name == region:
            country_code = code
            break
    
    # Get items for this country
    if country_code:
        items = (Item.objects
                 .filter(order__user__profile__country=country_code)
                 .select_related('movie')
                 .values('movie__id', 'movie__name', 'movie__price')
                 .annotate(total_purchases=Sum('quantity'))
                 .order_by('-total_purchases')[:10])
    else:
        items = []
    
    template_data = {
        'title': f'Trending in {region}',
        'region': region,
        'trending_movies': items,
    }
    return render(request, 'movies/trending_region.html', {'template_data': template_data})