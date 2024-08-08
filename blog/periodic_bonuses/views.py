from django.shortcuts import render, redirect
from periodic_bonuses.api.utils import CalculateNextBonus


def get_periodic_bonus(request, pk):
    bonus_obj = CalculateNextBonus(request=request, periodic_bonus_id=pk)
    if bonus_obj.check_bonus():
        bonus_obj.getting_bonus()
        return redirect('/my/profile/')
    return redirect('/my/profile/')