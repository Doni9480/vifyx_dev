from rest_framework import serializers


def check_language(language):
    if language not in ['russian', 'english']:
        raise serializers.ValidationError('Invalid language.')