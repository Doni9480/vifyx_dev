from django.utils.timezone import timedelta, now
from rest_framework import serializers
from periodic_bonuses.models import PeriodicBonuses, ReceivingPeriodicPoints
from periodic_bonuses.api.utils import CalculateNextBonus


class PeriodicBonusesSerializer(serializers.ModelSerializer):
    timer = serializers.SerializerMethodField()
    
    class Meta:
        model = PeriodicBonuses
        fields = (
            "id", 
            "title",
            "description",
            "scores",
            "timer"
        )
    
    def get_timer(self, obj, *args, **kwargs):
        request = self.context.get("request", None)
        if request is None:
            raise TypeError("User is not specified")
        bonus_obj = CalculateNextBonus(request=request, periodic_bonus_id=obj.id)
        return bonus_obj.calculate_next_bonus()

# class ReceivingPeriodicPointsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ReceivingPeriodicPoints
#         fields = (
#             "user",
#             "periodic_bonus",
#             "received_date",
#         )
        
