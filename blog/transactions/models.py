from typing import Iterable
from django.conf import settings
from django.db import models
from users.models import User
from campaign.models import Task
from campaign.models import UserTaskChecking


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
        max_length=255,
        choices=STATUS_CHOICES,
        default=STATUS_CREATED,
        verbose_name="Status",
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
            return User.objects.create_user(
                username="system", email="system@gmail.com", password="system"
            )

    @staticmethod
    def information_generation(info: dict, from_user: User, to_user: User):
        options = {
            "task": [
                "Transfer for completed task",
                "Topping up the account for a completed task",
            ],
            "referral": [
                "Transfer for registration via a referral link",
                "Replenishment of the account for registration via a referral link",
            ],
            "telegram_wallet": [
                "Transfer for connecting telegram wallet",
                "Reward for connecting telegram wallet",
            ],
            "twitter_account": [
                "Reward for connecting a Twitter account",
                "Reward for connecting a Twitter account",
            ],
            "periodic_bonus": [
                "Transfer of a periodic bonus",
                "Getting periodic bonuses",
            ],
        }

        users_info = {}
        users_info["translation"] = info
        users_info["clients"] = []
        for ix, obj in enumerate([from_user, to_user]):
            users_info["clients"].append(
                {
                    "id": obj.id,
                    "username": obj.username,
                    "message": options[info.get("type")][ix],
                }
            )
        return users_info

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
            info=Transactions.information_generation(
                info, from_user_object, to_user_object
            ),
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
            info=Transactions.information_generation(info, system_user, user_object),
            status=Transactions.STATUS_COMPLETED,
        )

        return transaction

    @staticmethod
    def create_translation_for_completing_tasks(
        from_user: str | User,
        to_user: str | User,
        amount: int,
        task_checking_obj: UserTaskChecking,
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
            info=Transactions.information_generation(
                {
                    "type": "task",
                    "pk": task_checking_obj.task.id,
                    "title": task_checking_obj.task.name,
                    "description": task_checking_obj.task.description,
                    "check_object_pk": task_checking_obj.pk,
                    "received": task_checking_obj.is_received,
                },
                from_user_object,
                to_user_object,
            ),
            status=Transactions.STATUS_AWAITING,
        )

        return transaction

    @staticmethod
    def update_translation_for_completing_tasks(task_checking_obj: UserTaskChecking):
        transaction = Transactions.objects.filter(
            info__translation__received=False,
            info__translation__check_object_pk=task_checking_obj.pk,
        )
        if transaction.exists():
            transaction = transaction.first()
            transaction.info["translation"]["received"] = True
            transaction.save()

    def check_is_system_user(self, user):
        return user.username == "system"

    def execution_of_the_transaction(self):
        if self.status == Transactions.STATUS_CREATED:
            if self.info["translation"].get("type") == "task":
                if not self.info["translation"]["received"]:
                    self.operation_steps(step="from")
                    self.status == Transactions.STATUS_AWAITING
            else:
                self.operation_steps(step="all")
                self.status = Transactions.STATUS_COMPLETED
        elif self.status == Transactions.STATUS_AWAITING:
            if self.info["translation"].get("type") == "task":
                if self.info["translation"]["received"]:
                    self.operation_steps(step="to")
                    self.status = Transactions.STATUS_COMPLETED

    def operation_steps(self, step="all"):
        if step == "all":
            if not self.check_is_system_user(self.from_user):
                self.from_user.scores -= self.amount
                self.from_user.save()
            if not self.check_is_system_user(self.to_user):
                self.to_user.scores += self.amount
                self.to_user.save()
        elif step == "from":
            if not self.check_is_system_user(self.from_user):
                self.from_user.scores -= self.amount
                self.from_user.save()
        elif step == "to":
            if not self.check_is_system_user(self.to_user):
                self.to_user.scores += self.amount
                self.to_user.save()

    def save(self, *args, **kwargs) -> None:
        self.execution_of_the_transaction()
        return super().save(*args, **kwargs)
