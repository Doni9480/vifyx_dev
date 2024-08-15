from rest_framework import serializers
from albums.models import Album, AlbumPhoto, Subcategory, DraftAlbum, DraftAlbumPhoto
from notifications.models import Notification, NotificationBlog
from blog.validators import check_language
from blogs.models import LevelAccess, BlogFollow


class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = (
            "id",
            "subcategory_rus",
            "subcategory_eng",
        )
        
        
class AlbumDeletedPhotoSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    
    class Meta:
        model = AlbumPhoto
        fields = [
            'id'
        ]


class AlbumPhotoSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    
    class Meta:
        model = AlbumPhoto
        fields = [
            'id',
            'photo',
        ]
        

class AlbumPhotoShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlbumPhoto
        fields = [
            'id',
            'album',
            'photo',
        ]
        
        
class AlbumShowSerializer(serializers.ModelSerializer):   
    class Meta:
        model = Album
        fields = (
            "id",
            "preview",
            "title",
            "language",
            "category",
            "subcategory",
            "user",
            "date"
        )
        

class AlbumSerializer(serializers.ModelSerializer):
    photos_set = AlbumPhotoSerializer(source="photos", many=True, required=True)
    deleted_photos_set = AlbumDeletedPhotoSerializer(source="deleted_photos", many=True, required=False)
    language = serializers.CharField(required=False, validators=[check_language])
    
    class Meta:
        model = Album
        fields = (
            "preview",
            "title",
            "description",
            "photos_set",
            "deleted_photos_set",
            "language",
            "category",
            "subcategory",
            "blog",
            "level_access",
        )
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", 1)
        self._instance = kwargs.get("instance", None)
        super().__init__(*args, **kwargs)
        
    def validate(self, attrs):
        try:
            if self._instance:
                if attrs.get('category') and not attrs.get('subcategory'):
                    raise Exception()
            subcategory = attrs['subcategory']
            category = attrs['category']
            if subcategory.category != category:
                raise Exception()
        except Exception:
            raise serializers.ValidationError({"subcategory": "Invalid subcategory."})
        
        if attrs.get("blog") and self._instance:
            del attrs["blog"]
            
        level_access = attrs.get('level_access')
        if level_access:
            if self._instance:
                blog = self._instance.blog
            else:
                blog = attrs['blog']
            if not LevelAccess.objects.filter(id=level_access.pk, blog=blog):
                raise serializers.ValidationError({'level_access': 'Invalid level access.'})
        
        return attrs
    
    def create(self, validated_data):
        photos_data = validated_data.get("photos", [])
        if photos_data:
            del validated_data['photos']
            
        album = Album(**validated_data)
        album.user = self.user
        album.save()
        for photo_data in photos_data:
            photo_data['album'] = album
            AlbumPhoto.objects.create(**photo_data)
        
        return album
    
    def update(self, album, validated_data):
        photos_data = validated_data.get("photos", [])
        if photos_data:
            del validated_data['photos']
        deleted_photos_data = validated_data.get("deleted_photos", [])
        if deleted_photos_data:
            del validated_data['deleted_photos']
            
        if not validated_data.get('level_access'):
            album.level_access = None
            
        for attr, value in validated_data.items():
            setattr(album, attr, value)
        album.save()
        
        for deleted_photo in deleted_photos_data:
            album_photo = AlbumPhoto.objects.filter(id=deleted_photo['id']).first()
            if album_photo:
                album_photo.delete()
        for photo_data in photos_data:
            photo_data['album'] = album
            AlbumPhoto.objects.create(**photo_data)
            
        return album
        
    def save(self):
        album = super(AlbumSerializer, self).save()
        
        if (
            not self._instance and not album.level_access
        ):  # if this not edit to survey and album is free
            follows = BlogFollow.objects.filter(blog=album.blog)
            for follow in follows:
                if follow.follower.is_notificated:
                    if NotificationBlog.objects.filter(
                        follower=follow.follower, blog=album.blog, user=album.user, get_notifications_blog=True
                    ):
                        Notification.objects.create(album=album, user=follow.follower)
        return album
    

class DraftAlbumPhotoSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    
    class Meta:
        model = DraftAlbumPhoto
        fields = [
            'id',
            'photo',
        ]


class DraftSerializer(serializers.ModelSerializer):
    photos_set = DraftAlbumPhotoSerializer(source="photos", many=True, required=False)
    deleted_photos_set = AlbumDeletedPhotoSerializer(source="deleted_photos", many=True, required=False)
    language = serializers.CharField(required=False, validators=[check_language])
    
    class Meta:
        model = DraftAlbum
        fields = (
            "preview",
            "title",
            "description",
            "photos_set",
            "deleted_photos_set",
            "language",
            "category",
            "subcategory",
            "blog",
            "level_access",
        )
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", 1)
        self._instance = kwargs.get("instance", None)
        super().__init__(*args, **kwargs)
        
    def create(self, validated_data):
        photos_data = validated_data.get("photos", [])
        if photos_data:
            del validated_data['photos']
            
        draft_album = DraftAlbum(**validated_data)
        draft_album.user = self.user
        draft_album.save()
        for photo_data in photos_data:
            photo_data['draft_album'] = draft_album
            DraftAlbumPhoto.objects.create(**photo_data)
        
        return draft_album
    
    def update(self, draft_album, validated_data):
        photos_data = validated_data.get("photos", [])
        if photos_data:
            del validated_data['photos']
        deleted_photos_data = validated_data.get("deleted_photos", [])
        if deleted_photos_data:
            del validated_data['deleted_photos']
            
        if not validated_data.get('level_access'):
            draft_album.level_access = None
            
        for attr, value in validated_data.items():
            setattr(draft_album, attr, value)
        draft_album.save()
        
        for deleted_photo in deleted_photos_data:
            draft_album_photo = DraftAlbumPhoto.objects.filter(id=deleted_photo['id']).first()
            if draft_album_photo:
                draft_album_photo.delete()
        for photo_data in photos_data:
            photo_data['draft_album'] = draft_album
            DraftAlbumPhoto.objects.create(**photo_data)
            
        return draft_album
        

class AlbumIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = (
            "id",
            "slug",
            "preview",
            "title",
            "language",
            "user",
            "date",
        )


class AlbumNoneSerializer(serializers.Serializer):
    pass