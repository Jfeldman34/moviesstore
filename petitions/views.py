from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from .models import Petition, PetitionVote
from .forms import PetitionForm, VoteForm

def index(request):
    """Display all active petitions with voting stats"""
    petitions_list = Petition.objects.annotate(
        total_votes=Count('votes'),
        yes_votes=Count('votes', filter=Q(votes__value=True)),
        no_votes=Count('votes', filter=Q(votes__value=False))
    ).order_by('-created_at')
    
    paginator = Paginator(petitions_list, 10)
    page_number = request.GET.get('page')
    petitions = paginator.get_page(page_number)
    
    return render(request, 'petitions/index.html', {
        'template_data': {'title': 'Movie Petitions'},
        'petitions': petitions
    })


def show(request, petition_id):
    """Display a single petition and handle voting"""
    petition = get_object_or_404(Petition, id=petition_id)
    votes = petition.votes.select_related('user').order_by('-voted_at')

    user_vote = None
    if request.user.is_authenticated:
        user_vote = PetitionVote.objects.filter(petition=petition, user=request.user).first()

    if request.method == 'POST' and request.user.is_authenticated:
        if user_vote:
            messages.warning(request, 'You have already voted on this petition.')
            return redirect('petitions.show', petition_id=petition.id)

        form = VoteForm(request.POST)
        if form.is_valid():
            vote = form.save(commit=False)
            vote.petition = petition
            vote.user = request.user
            vote.save()
            vote_type = "Yes" if vote.value else "No"
            messages.success(request, f'Your "{vote_type}" vote has been recorded!')
            return redirect('petitions.show', petition_id=petition.id)
    else:
        form = VoteForm()

    return render(request, 'petitions/show.html', {
        'template_data': {'title': f'Petition: {petition.title}'},
        'petition': petition,
        'votes': votes,
        'user_vote': user_vote,
        'form': form
    })


@login_required
def create(request):
    """Create a new petition"""
    if request.method == 'POST':
        form = PetitionForm(request.POST)
        if form.is_valid():
            petition = form.save(commit=False)
            petition.created_by = request.user
            petition.save()
            messages.success(request, 'Your petition has been created successfully!')
            return redirect('petitions.show', petition_id=petition.id)
    else:
        form = PetitionForm()
    
    return render(request, 'petitions/create.html', {
        'template_data': {'title': 'Create Movie Petition'},
        'form': form
    })


@login_required
def my_petitions(request):
    """Display current user's petitions"""
    petitions_list = Petition.objects.filter(created_by=request.user).annotate(
        total_votes=Count('votes'),
        yes_votes=Count('votes', filter=Q(votes__value=True)),
        no_votes=Count('votes', filter=Q(votes__value=False))
    ).order_by('-created_at')
    
    paginator = Paginator(petitions_list, 10)
    page_number = request.GET.get('page')
    petitions = paginator.get_page(page_number)
    
    return render(request, 'petitions/my_petitions.html', {
        'template_data': {'title': 'My Petitions'},
        'petitions': petitions
    })


@login_required
def delete_petition(request, petition_id):
    """Delete a petition (only by creator)"""
    petition = get_object_or_404(Petition, id=petition_id, created_by=request.user)
    
    if request.method == 'POST':
        petition.delete()
        messages.success(request, 'Your petition has been deleted.')
        return redirect('my_petitions')
    
    return render(request, 'petitions/delete_confirm.html', {
        'template_data': {'title': 'Delete Petition'},
        'petition': petition
    })
