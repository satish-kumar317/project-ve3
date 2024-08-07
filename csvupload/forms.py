from django import forms

class UploadFileform(forms.Form):
    file = forms.FileField()
