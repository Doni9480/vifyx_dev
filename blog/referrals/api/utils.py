from django.shortcuts import get_object_or_404
from users.models import User
from referrals.models import Referral


class ReferralHandler(object):

    def __init__(self, request):
        self.answer = {"referrer": None, "message": None}
        self.request = request
        self.referral_code = self._get_referral_code()
        self.referral_owner = self._check_referral_code_owner()

    def _get_referral_code(self):
        if "referral_code" in self.request.POST:
            return self.request.POST["referral_code"]
        self.answer.update({"message": "No referral code found."})
        return None

    def _check_referral_code_owner(self):
        if self.referral_code:
            return get_object_or_404(User, referral_code=self.referral_code)
        self.answer.update({"message": "Invalid or expired referral code."})
        return None

    def save(self, new_user=None):
        if self.referral_owner:
            if new_user and isinstance(new_user, User):
                Referral.objects.create(user=new_user, referral=self.referral_owner)
            elif new_user and isinstance(new_user, int):
                user = get_object_or_404(User, pk=new_user)
                Referral.objects.create(user=user, referral=self.referral_owner)
            self.answer.update({"message": "Referral has been added."})
        return self.answer
