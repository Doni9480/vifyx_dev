from django.utils.timezone import now, timedelta
from periodic_bonuses.models import PeriodicBonuses, ReceivingPeriodicPoints


class CalculateNextBonus(object):
    object_periodic_bonus = None
    list_user_bonus = None
    last_not_received_bonus = None
    last_received_bonus = None

    def __init__(self, request, periodic_bonus_id=None):
        self.request = request
        self.user = self.request.user
        self.periodic_bonus_id = periodic_bonus_id

        self.__init_objects()

    def __init_objects(self):
        self.get_periodic_bonus()
        self.get_list_user_bonus()
        self.get_last_not_received_bonus()
        self.get_last_received_bonus()

    def get_periodic_bonus(self):
        periodic_bonuses = PeriodicBonuses.objects.filter(pk=self.periodic_bonus_id)
        if periodic_bonuses.exists():
            self.object_periodic_bonus = periodic_bonuses.first()
        return self.object_periodic_bonus

    def get_list_user_bonus(self):
        self.list_user_bonus = ReceivingPeriodicPoints.objects.filter(
            periodic_bonus=self.object_periodic_bonus, user=self.user
        )
        if not self.list_user_bonus.exists():
            obj = ReceivingPeriodicPoints()
            obj.user = self.user
            obj.periodic_bonus = self.object_periodic_bonus
            # obj.is_received = True
            # obj.received_date = now()
            obj.save()
            return self.get_list_user_bonus()
        return self.list_user_bonus

    def get_last_not_received_bonus(self):
        not_received_bonuses = self.list_user_bonus.filter(is_received=False)
        if not_received_bonuses.exists():
            self.last_not_received_bonus = not_received_bonuses.order_by(
                "created_at"
            ).first()
        return self.last_not_received_bonus

    def get_last_received_bonus(self):
        received_bonuses = self.list_user_bonus.filter(is_received=True)
        if received_bonuses.exists():
            self.last_received_bonus = received_bonuses.order_by("created_at").first()
        return self.last_received_bonus

    def get_time(self):
        if self.last_received_bonus:
            return self.last_received_bonus.received_date + timedelta(
                hours=self.object_periodic_bonus.interval
            )
        else:
            return self.last_not_received_bonus.created_at + timedelta(
                hours=self.object_periodic_bonus.interval
            )

    def calculate_next_bonus(self):
        next_bonus_time = self.get_time()
        if next_bonus_time > now():
            t_seconds = (next_bonus_time - now()).total_seconds()
            hours = int(t_seconds // 3600)
            minutes = int((t_seconds % 3600) // 60)
            seconds = int(t_seconds % 60)
            return f"{hours}:{minutes}:{seconds}"
        else:
            return "00:00:00"

    def check_bonus(self):
        next_bonus_time = self.get_time()
        if next_bonus_time > now():
            return False
        else:
            return True

    def getting_bonus(self):
        next_bonus_time = self.get_time()
        if next_bonus_time > now():
            timer = self.calculate_next_bonus()
            return f"Time until next bonus: {timer}"
        else:
            self.last_not_received_bonus.receiving_periodic_bonus()
            return "Received"
