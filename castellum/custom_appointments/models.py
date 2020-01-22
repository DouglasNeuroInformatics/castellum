from django.contrib.auth import get_user_model
from django.db import models
from projects.models.membership import BaseMembership

class Project(models.Model):
    name = models.CharField(max_length=120)


class Membership(BaseMembership):

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='my_memberships')
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    is_coordinator = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} is member in project {self.project.name}'
