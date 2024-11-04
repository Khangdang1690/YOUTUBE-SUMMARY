from django import forms

class YoutubeLinkForm(forms.Form):
  youtube_url = forms.URLField(label="YouTube URL", required=True)