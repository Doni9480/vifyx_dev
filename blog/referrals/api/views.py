from django.shortcuts import render
from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.decorators import action
from rest_framework.response import Response

from blog.referrals.api.serializers import ReferralSerializer
from referrals.models import Referral


# Create your views here.
class ReferralViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    queryset = Referral.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ReferralSerializer

    # def create(self, request, *args, **kwargs):
    #     serializer = ReferralSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save(user=request.user)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     else:
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(code=request.user.referral_code)
        serializer = ReferralSerializer(queryset, many=True)
        return serializer.data

    # @action(detail=False, methods=["get"], url_path=r"referral/")
    # def get_referral_link(self, request, *args, **kwargs):
    #     referral_link = (
    #         f"{request.build_absolute_uri()}/referral/{self.kwargs['referral_code']}"
    #     )
    #     return Response({"referral_link": referral_link})
