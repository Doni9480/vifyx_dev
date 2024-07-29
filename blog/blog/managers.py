from django.db import models


class LevelAccessManager(models.Manager):
    def get_queryset(self):
        return super(LevelAccessManager, self).get_queryset().filter(level_access=None)
    
    
class TestShowManager(models.Manager): # for tests
    def get_queryset(self):
        return super(TestShowManager, self).get_queryset().filter(hidden=False)