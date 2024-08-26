from django.db import models
from users.models import User
from campaign.models import Task


class Referral(models.Model):
    referral_user = models.ForeignKey(
        User, related_name="referred", on_delete=models.CASCADE, verbose_name="User"
    )
    code = models.CharField(max_length=20, verbose_name="Code")
    tasks_completed = models.IntegerField(default=0, verbose_name="Task Completed")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    def __str__(self):
        return f"{self.referral_user}"

    class Meta:
        verbose_name = "Referral"
        verbose_name_plural = "Referrals"

    def first_task_user(self) -> Task | None:
        first_completed_task = self.referral_user.usertaskchecking_set
        user_task = (
            first_completed_task.first().task
            if first_completed_task.count() == 1
            else None
        )
        return user_task

    def save(self, *args, **kwargs):
        if self.pk:
            # Сохранение старых значений перед вызовом save()
            old_instance = Referral.objects.get(pk=self.pk)
            self.old__tasks_completed = old_instance.tasks_completed
        super(Referral, self).save(*args, **kwargs)


class BonusCoefficients(models.Model):
    from_num = models.PositiveIntegerField("From")
    to_num = models.PositiveIntegerField("To")
    coefficient = models.FloatField("Coefficient")

    class Meta:
        verbose_name = "Bonus coefficient"
        verbose_name_plural = "Bonus coefficients"

    def __str__(self):
        return f"{self.from_num} - {self.to_num} > {self.coefficient}"

    @staticmethod
    def get_coefficient(number_of_users):
        bonus = BonusCoefficients.objects.filter(
            from_num__lte=number_of_users, to_num__gte=number_of_users
        ).first()
        return float(bonus.coefficient) if bonus else 1.0
