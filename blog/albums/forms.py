from django import forms
from albums.models import Album, DraftAlbum


class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = (
            "preview",
            "title",
        )
        
        
class DraftAlbumForm(forms.ModelForm):
    class Meta:
        model = DraftAlbum
        fields = (
            "preview",
            "title",
            "blog",
        )