from django.shortcuts import get_object_or_404
import requests
from users.models import User
from referrals.models import Referral


class ReferralHandler(object):

    def __init__(self, request):
        self.answer = {"referrer": None, "message": None}
        self.request = request
        self.referral_code = self._get_referral_code()
        self.referral_owner = self._check_referral_code_owner()

    def _get_referral_code(self):
        if "referral_code" in self.request.query_params.keys():
            return self.request.query_params.get("referral_code")
        self.answer.update({"message": "No referral code found."})
        return None

    def _check_referral_code_owner(self):
        if self.referral_code:
            owner_usr = User.objects.filter(referral_code=self.referral_code)
            print("Checking lis", owner_usr)
            if owner_usr:
                print("Checking finish!!!", owner_usr)
                return owner_usr.first()
            self.answer.update({"message": "Invalid or expired referral code."})
        self.answer.update({"message": "Invalid or expired referral code."})
        return None

    def save(self, new_user=None):
        if self.referral_owner:
            if new_user and isinstance(new_user, User):
                r = Referral(referral_user=new_user, code=self.referral_code)
                r.save()
            elif new_user and isinstance(new_user, dict):
                user = User.objects.filter(email=new_user["email"]).first()
                r = Referral(referral_user=user, code=self.referral_code)
                r.save()
            self.answer.update({"message": "Referral has been added."})
        return self.answer
