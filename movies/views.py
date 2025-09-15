from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()
    template_data = {}
   
    top_reviews = Review.objects.order_by('-rating')[:5]
    recent_reviews = Review.objects.order_by('-date')[:5]
    template_data['top_reviews'] = top_reviews
    pop_reviews = Review.objects.annotate(num_likes=Count('liked_users')).order_by('-num_likes')[:5]
    template_data['pop_reviews'] = pop_reviews
    template_data['recent_reviews'] = recent_reviews
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    top_movies = Movie.objects.annotate(
    times_ordered=Sum('item__quantity') 
    ).order_by('-times_ordered')[:3]  
    recent_movies = Movie.objects.order_by('-date')[:3]
    ## the __ allows you to access fields of a different model
    top_movies_by_rating = Movie.objects.annotate(
    avg_rating=Avg('review__rating')
    ).order_by('-avg_rating')[:3]
    template_data['top_movies'] = top_movies
    template_data['top_movies_by_rating'] = top_movies_by_rating
    return render(request, 'movies/index.html',
                  {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie)
    top_review = reviews.order_by('-rating').first()
    
    template_data = {
        'title': movie.name,
        'movie': movie,
        'reviews': reviews,
        'top_review': top_review
    }
    return render(request, 'movies/show.html', {'template_data': template_data})


@login_required
def like_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    # Only allow one like per user
    if request.user not in review.liked_users.all():
        review.liked_users.add(request.user)
        review.popularity += 1    # increment the popularity
        review.save()

    return redirect('movies.show', id=review.movie.id)


    
@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment']  != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        rating = request.POST.get('rating')
        if rating: 
            review.rating = int(rating)
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
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html',
            {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)
    

    
@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id,
        user=request.user)
    review.delete()
    return redirect('movies.show', id=id)
