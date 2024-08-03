from django.db import models
from users.models import User


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
        
    def save(self, *args, **kwargs):
        if self.pk:
            # Сохранение старых значений перед вызовом save()
            old_instance = Referral.objects.get(pk=self.pk)
            self.old__tasks_completed = old_instance.tasks_completed
        super(Referral, self).save(*args, **kwargs)
