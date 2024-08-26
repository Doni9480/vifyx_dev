from django.db import models
from solo.models import SingletonModel

CONSTANCE_CONFIG = {
    'LIMIT_CAMPAIGN': (10, 'Лимит компаний для одного пользователя'),
    'PERIODIC_SCORES': (100, 'Количество баллов периодического бонуса'),
    'TWITTER_CONNECT_SCORES': (150, 'Баллы за подключения Twitter аккаунта'),
    'TELEGRAM_WALLET_CONNECT_SCORES': (200, 'Баллы за подключение кошелька Telegram'),
    'POINT_INVITATION_BY_REFERRAL_LINK': (500, 'Награда (в баллах) за каждого приглашенного пользователя по реферальной ссылке'),
}

class SiteConfiguration(SingletonModel): # (models.Model):
    limit_campaign = models.PositiveIntegerField(default=10, verbose_name="Лимит компаний для одного пользователя")
    periodic_scores = models.PositiveIntegerField(default=100, verbose_name="Количество баллов периодического бонуса")
    twitter_connect_scores = models.PositiveIntegerField(default=150, verbose_name="Баллы за подключения Twitter аккаунта")
    telegram_wallet_connect_scores = models.PositiveIntegerField(default=200, verbose_name="Баллы за подключение кошелька Telegram")
    point_invitation_by_referral_link = models.PositiveIntegerField(default=500, verbose_name="Награда (в баллах) за каждого приглашенного пользователя по реферальной ссылке")

    def __str__(self):
        return "Site Configuration"

    class Meta:
        verbose_name = "Site Configuration"
        verbose_name_plural = "Site Configurations"