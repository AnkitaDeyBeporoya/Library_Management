from django import forms 
from .models import userdata, bookdata, borrowrecord
from datetime import date, timedelta

class userdataform(forms.ModelForm):
    address = forms.CharField(required=False)
    class Meta:
        model = userdata
        fields = ['full_name', 'email', 'phone_no', 'address']

class bookdataform(forms.ModelForm):
    class Meta:
        model = bookdata
        fields = ['book_name', 'author', 'type', 'stock']

class borroerecordForm(forms.ModelForm):

    class Meta:
        model = borrowrecord
        fields = ['user', 'book', 'issue_date', 'return_date']

def __init__(self):
    self.fields['user'].queryset = userdata.objects.all()
    self.fields['book'].queryset = bookdata.objects.all()

    today = date.today()
    self.fields['issue_date'].initial = today
    self.fields['return_date'].initial = today + timedelta(days=7)