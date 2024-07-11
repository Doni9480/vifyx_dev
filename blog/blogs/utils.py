from django.utils import timezone
from django.db import transaction

from blog.utils import add_months

from blogs.models import PaidFollow

from users.models import User, Percent


@transaction.atomic
def paid_follows():
    present = timezone.now()
    paid_follows = PaidFollow.objects.all()
    for paid_follow in paid_follows:
        if paid_follow.date <= present:
            user = paid_follow.blog.user
            if user.is_autorenewal:
                blog = paid_follow.blog
                price = paid_follow.count_months * paid_follow.blog_access_level.scores
                follower = paid_follow.follower
                follower.scores -= price

                if follower.scores < 0:
                    paid_follow.delete()
                else:
                    follower.save()

                    admin = User.objects.filter(is_superuser=True)[0]
                    percent = Percent.objects.all()[0].percent / 100
                    admin.scores += int(price * percent) or 1
                    admin.save()

                    reverse_percent = 1 - percent
                    blog.user.scores = int(price * reverse_percent) or 1
                    blog.user.save()

                    paid_follow.date = add_months(
                        paid_follow.date, paid_follow.count_months
                    )
                    paid_follow.save()
            else:
                paid_follow.delete()
