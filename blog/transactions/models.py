from django.conf import settings
from django.db import models
from users.models import User
from campaign.models import Task


class Transactions(models.Model):
    STATUS_CREATED = "created"
    STATUS_AWAITING = "awaiting receipt confirmation"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = (
        (STATUS_CREATED, "Created"),
        (STATUS_AWAITING, "Awaiting receipt confirmation"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_FAILED, "Failed"),
    )
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="transactions",
        on_delete=models.CASCADE,
        verbose_name="From User",
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="receiving_transactions",
        on_delete=models.CASCADE,
        verbose_name="To User",
    )
    amount = models.PositiveIntegerField(verbose_name="Amount")
    info = models.JSONField(verbose_name="Info")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Date")
    status = models.CharField(
        max_length=255, choices=STATUS_CHOICES, verbose_name="Status"
    )

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __str__(self):
        return f"{self.from_user} -> {self.to_user} - {self.amount}"

    @staticmethod
    def get_or_create_system_user_object():
        try:
            return User.objects.get(username="system")
        except User.DoesNotExist:
            return User.objects.create_user(username="system", password="system")

    @staticmethod
    def create_translation_between_users(
        from_user: str | User,
        to_user: str | User,
        amount: int,
        info: dict,
    ):
        from_user_object = (
            from_user
            if isinstance(from_user, User)
            else User.objects.get(username=from_user)
        )
        to_user_object = (
            to_user if isinstance(to_user, User) else User.objects.get(username=to_user)
        )

        transaction = Transactions.objects.create(
            from_user=from_user_object,
            to_user=to_user_object,
            amount=amount,
            info=info,
            status=Transactions.STATUS_COMPLETED,
        )

        return transaction

    @staticmethod
    def create_system_transaction(
        user: str | User,
        amount: int,
        info: dict,
    ):
        system_user = Transactions.get_or_create_system_user_object()
        user_object = (
            user if isinstance(user, User) else User.objects.get(username=user)
        )

        transaction = Transactions.objects.create(
            from_user=system_user,
            to_user=user_object,
            amount=amount,
            info=info,
            status=Transactions.STATUS_COMPLETED,
        )

        return transaction

    @staticmethod
    def create_translation_for_completing_tasks(
        from_user: str | User,
        to_user: str | User,
        amount: int,
        task_obj: Task | int,
    ):
        from_user_object = (
            from_user
            if isinstance(from_user, User)
            else User.objects.get(username=from_user)
        )
        to_user_object = (
            to_user if isinstance(to_user, User) else User.objects.get(username=to_user)
        )

        transaction = Transactions.objects.create(
            from_user=from_user_object,
            to_user=to_user_object,
            amount=amount,
            info={
                "type": "task",
                "pk": task_obj.id,
                "title": task_obj.name,
                "description": task_obj.description,
                "received": False
            },
            status=Transactions.STATUS_AWAITING,
        )

        return transaction

    # create_translation_for_completing_tasks