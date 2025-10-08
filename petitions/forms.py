from django import forms
from .models import Petition, PetitionVote

class PetitionForm(forms.ModelForm):
    """Form for creating/editing a Petition."""
    class Meta:
        model = Petition
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter petition title',
                'maxlength': '255'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe why this movie should be added (optional)...',
                'rows': 4
            }),
        }
        labels = {
            'title': 'Petition Title',
            'description': 'Description (optional)',
        }

    def clean_title(self):
        title = self.cleaned_data.get('title', '') or ''
        title = title.strip()
        if not title:
            raise forms.ValidationError("Title is required.")
        if len(title) < 5:
            raise forms.ValidationError("Title must be at least 5 characters.")
        return title


class VoteForm(forms.ModelForm):
    """Form for casting a vote. Matches PetitionVote.value (boolean)."""
    VOTE_CHOICES = [
        ('True', 'Yes — I want this movie added!'),
        ('False', "No — I don't want this movie added"),
    ]

    value = forms.ChoiceField(
        choices=VOTE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Your Vote'
    )

    class Meta:
        model = PetitionVote
        fields = ['value']

    def clean_value(self):
        """Convert 'True'/'False' string into a Python bool."""
        val = self.cleaned_data.get('value')
        return True if val == 'True' else False
