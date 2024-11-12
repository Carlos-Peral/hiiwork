from django.db import models
from talentSite.storage_backends import PublicMediaStorage


class Badge(models.Model):
    name = models.CharField(max_length=50)

    def upload_to_path(self, filename):
        url = "badges/%s" % (str(self.id), filename)
        return url
    image = models.ImageField(
        storage=PublicMediaStorage(), upload_to=upload_to_path)
    description = models.TextField(default='')
    tier = models.IntegerField(default=1, blank=False, null=False)

    def __str__(self):
        return self.name
