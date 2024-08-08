from rest_framework import serializers

from django.contrib import auth

from users.models import User, Token, Hide

from blogs.models import Blog, PaidFollow, BlogFollow


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8)
    password2 = serializers.CharField(write_only=True)
    referrer_code = serializers.CharField(write_only=True, required=False)
    language = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = (
            "first_name",
            "email",
            "username",
            "password",
            "password2",
            "language",
            "referrer_code",
        )
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def save(self):
        languages_dict = {'en': 'english', 'ru': 'russian'}
        if languages_dict.get(self.validated_data.get('language', ''), ''):
            self.validated_data['language'] = languages_dict[self.validated_data['language']]
        else:
            self.validated_data['language'] = 'any'
        self.user = User(
            first_name=self.validated_data["first_name"],
            email=self.validated_data["email"],
            username=self.validated_data["username"],
            language=self.validated_data['language'],
        )

        self.user.set_password(self.validated_data["password"])
        self.user.save()

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "Passwords must match."})

        return data

    def generate_key(self):
        token = Token.generate_key()
        Token.objects.create(key=token, user=self.user)
        return token


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        if username and password:
            user = auth.authenticate(
                request=self.context.get("request"),
                username=username,
                password=password,
            )

            if not user:
                msg = "Unable to log in with provided credentials."
                raise serializers.ValidationError({"password": msg})
        else:
            msg = 'Must include "username" and "password".'
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs

    def generate_key(self):
        user = self.validated_data["user"]

        token = Token.generate_key()
        user_token = Token.objects.filter(user_id=user)
        if not user_token:
            Token.objects.create(user=user, key=token)
        else:
            user_token.update(key=token)
        return token


class ScoresSerializer(serializers.Serializer):
    scores = serializers.IntegerField()


class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = (
            'id',
            'preview',
            'title',
        )
        

class PaidFollowSeriailzer(serializers.ModelSerializer):
    class Meta:
        model = PaidFollow
        

class BlogFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogFollow
        fields = ("blog",)


class HideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hide
        fields = (
            "user",
        )
        
        
class TwitterAccountUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("twitter",)


class TelegramWalletUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("telegram_wallet",)


class EditProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "first_name",
        )
        
        
class EditPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8)
    password2 = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = (
            "password",
            "password2",
        )
        
    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return attrs
        
    def update(self, user, validated_data):
        user.set_password(validated_data["password"])
        user.save()
        return user
