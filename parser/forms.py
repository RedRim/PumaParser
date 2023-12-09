from django import forms

class SearchForm(forms.Form):
    search_query = forms.CharField(label='', required=False, widget=forms.TextInput(attrs={'placeholder': 'Шукати...'}))
