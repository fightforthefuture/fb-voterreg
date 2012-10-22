from django import forms
from models import WONT_VOTE_REASONS, VotingBlock
from django.forms.util import ErrorList

class WontVoteForm(forms.Form):
    wont_vote_reason = forms.ChoiceField(
        widget=forms.RadioSelect, choices=WONT_VOTE_REASONS)

class VotingBlockForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(VotingBlockForm, self).clean()
        name = cleaned_data.get("organization_name")
        website = cleaned_data.get("organization_website")
        privacy_policy = cleaned_data.get("organization_privacy_policy")
        if name or website or privacy_policy:
            if not name:
                self.errors['organization_name'] = self.errors.get('organization_name') or  ErrorList()
                self.errors['organization_name'].append('Field is Required.')
            if not website:
                self.errors['organization_website'] = self.errors.get('organization_website') or  ErrorList()
                self.errors['organization_website'].append('Field is Required.')
            if not privacy_policy:
                self.errors['organization_privacy_policy'] = self.errors.get('organization_privacy_policy') or  ErrorList()
                self.errors['organization_privacy_policy'].append('Field is Required.')
        return cleaned_data

    class Meta:
        model = VotingBlock
        fields = ('name', 'description', 'icon', 'organization_name', 'organization_website', 'organization_privacy_policy')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Voting block name'}),
            'description': forms.TextInput(attrs={'placeholder': 'Description / share text'}),
            'organization_name': forms.TextInput(attrs={'placeholder': '"Organization Name"'}),
            'organization_website': forms.TextInput(attrs={'placeholder': 'Website'}),
            'organization_privacy_policy': forms.TextInput(attrs={'placeholder': 'Link to Privacy'})
        }




