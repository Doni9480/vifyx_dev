from django.utils.timezone import now, timedelta
from django.db import models


class PeriodicBonuses(models.Model):
    title = models.CharField(max_length=255, verbose_name="Title")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    scores = models.IntegerField(default=100, verbose_name="Scores")
    interval = models.PositiveIntegerField(
        help_text="Interval in hours", verbose_name="Interval"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")

    class Meta:
        verbose_name = "Periodic bonus"
        verbose_name_plural = "Periodic bonuses"

    def __str__(self):
        return self.title


class ReceivingPeriodicPoints(models.Model):
    user = models.ForeignKey(
        "users.User",
        related_name="receiving_periodic_points",
        on_delete=models.CASCADE,
        verbose_name="User",
    )
    periodic_bonus = models.ForeignKey(
        "PeriodicBonuses",
        related_name="receiving_periodic_points",
        on_delete=models.CASCADE,
        verbose_name="Periodic bonus",
    )
    received_date = models.DateTimeField(
        null=True, blank=True, verbose_name="received date"
    )
    is_received = models.BooleanField(default=False, verbose_name="is received")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="created at")

    class Meta:
        verbose_name = "Receiving periodic points"
        verbose_name_plural = "Receiving periodic points"

    def __str__(self):
        return f"{self.user}"

    def receiving_periodic_bonus(self):
        if not self.is_received:
            self.is_received = True
            self.received_date = now()
            self.save()
            self.__points_transfer()
            return True
        return False

    @staticmethod
    def create_next_bonus(last_bonus):
        bonus_obj = ReceivingPeriodicPoints()
        bonus_obj.user = last_bonus.user
        bonus_obj.periodic_bonus = last_bonus.periodic_bonus
        bonus_obj.save()
        return True

    def __points_transfer(self):
        self.user.scores += self.periodic_bonus.scores
        self.user.save()
        ReceivingPeriodicPoints.create_next_bonus(self)
        return True


