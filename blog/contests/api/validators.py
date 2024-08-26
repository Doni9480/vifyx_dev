from rest_framework import serializers


def check_item_type(item_type):
    if item_type not in ['post', 'album', 'quest']:
        raise serializers.ValidationError('Invalid item type.')
    
def check_criteries(criteries):
    if criteries not in ['likes', 'views', 'assessment']:
        raise serializers.ValidationError('Invalid criteries.')