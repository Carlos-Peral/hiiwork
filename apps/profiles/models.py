from django.db import models
from django.conf import settings
import uuid
from talentSite.storage_backends import PublicMediaStorage
from django.db.models.signals import post_save
from apps.badges.models import Badge
from apps.profiles.choices import *
from apps.gigs.models import Category

User = settings.AUTH_USER_MODEL


class UserProfile(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    firstName = models.CharField(max_length=50, default='', null=True)
    lastName = models.CharField(max_length=50, default='', null=True)
    buyerLevel = models.IntegerField(default=0)
    sellerLevel = models.IntegerField(default=0)
    badges = models.ManyToManyField(Badge, blank=True)
    buyerRating = models.IntegerField(default=0)
    sellerRating = models.IntegerField(default=0)
    city = models.CharField(
        max_length=2, choices=MX_CITY_CHOICES)
    userCategory1 = models.ForeignKey(
        Category, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(app_label)s_%(class)s_primary_category')
    userCategory2 = models.ForeignKey(
        Category, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(app_label)s_%(class)s_secondary_category')

    def generate_filename(self, filename):
        url = "%s/profileImage/%s" % (str(self.id), filename)
        return url
    profilePic = models.ImageField(
        storage=PublicMediaStorage(file_overwrite=True), upload_to=generate_filename, blank=True, null=True)

    def generate_filename_cover(self, filename):
        url = "%s/coverImage/%s" % (str(self.id), filename)
        return url
    coverImage = models.ImageField(
        storage=PublicMediaStorage(file_overwrite=True), upload_to=generate_filename_cover, blank=True, null=True)

    def __str__(self):
        return str(self.id)

    def get_uuid(self):
        return str(self.id)

    def get_fullname(self):
        return self.firstName + ' ' + self.lastName

    def get_displayable_name(self):
        if self.firstName != '':
            return self.firstName
        return self.user.username

    def get_user_categories(self):
        if self.userCategory1 is None:
            return ''
        if self.userCategory2 is None:
            return self.userCategory1
        else:
            return str(self.userCategory1) + '  \\  ' + str(self.userCategory2)

    def get_stars_as_buyer(self):
        if self.buyerRating is 0:
            return "-"
        return float(self.buyerRating)/10

    def get_stars_as_seller(self):
        if self.sellerRating is 0:
            return "-"
        return float(self.sellerRating)/10

    def get_city(self):
        return self.get_city_display()

    def get_profile_pic_url(self):
        return "https://hiiwork.s3.amazonaws.com/media/public/%s" % self.profilePic

    def get_portfolio_url(self):
        from django.urls import reverse
        return reverse('profile', kwargs={'username': self.user.username})


def create_profile(sender, **kwargs):
    if kwargs['created']:
        user_profile = UserProfile.objects.create(user=kwargs['instance'])


post_save.connect(create_profile, sender=User)
