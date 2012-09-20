from django import forms
from models import WONT_VOTE_REASONS

class WontVoteForm(forms.Form):
    wont_vote_reason = forms.ChoiceField(
        widget=forms.RadioSelect, choices=WONT_VOTE_REASONS)
