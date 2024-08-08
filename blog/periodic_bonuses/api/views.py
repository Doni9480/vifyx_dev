from django.shortcuts import render
from django.utils.timezone import now, timedelta
from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.decorators import action
from rest_framework.response import Response

from periodic_bonuses.models import PeriodicBonuses, ReceivingPeriodicPoints
from periodic_bonuses.api.utils import CalculateNextBonus
from .serializers import PeriodicBonusesSerializer


# Create your views here.
class ReceivingPeriodicPointsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = PeriodicBonuses.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = PeriodicBonusesSerializer

    def list(self, request, *args, **kwargs):
        serializer = PeriodicBonusesSerializer(
            self.get_queryset(), many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path=r"receiving_periodic_bonus/<pk>")
    def get_periodic_bonus(self, request, pk=None):
        bonus_obj = CalculateNextBonus(request=request, periodic_bonus_id=pk)
        if bonus_obj.check_bonus():
            return Response({"data": bonus_obj.getting_bonus()}, status=status.HTTP_200_OK)
        else:
            return Response({"data": bonus_obj.getting_bonus()}, status=status.HTTP_403_FORBIDDEN)