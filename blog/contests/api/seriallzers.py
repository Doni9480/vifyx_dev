from rest_framework import serializers
from contests.models import Contest


class ContestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contest
        fields = (
            'id',
            'preview',
            'title',
            'description',
            'start_date',
            'end_date',
            'language',
            'item_type',
            'criteries',
        )
        