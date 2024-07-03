from apscheduler.schedulers.background import BackgroundScheduler

from django.db.utils import ProgrammingError

from posts.utils import popular_blogs

from blogs.utils import paid_follows

from users.utils import send_scores
from users.models import TotalScore


class TasksScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()

    def run(self):
        if not self.scheduler.get_job(job_id="send_scores"):
            try:
                total_score = TotalScore.objects.all()
                if total_score:
                    self.scheduler.add_job(
                        send_scores,
                        "cron",
                        hour=total_score[0].hour,
                        minute=total_score[0].minute,
                        id="send_scores",
                    )
            except ProgrammingError:
                self.scheduler.add_job(
                    send_scores, "cron", hour=0, minute=0, id="send_scores"
                )

        # 2592000 - 30 days
        self.scheduler.add_job(popular_blogs, "interval", seconds=2592000)
        self.scheduler.add_job(paid_follows, "cron", hour=0, minute=0)
        self.scheduler.start()
