from django.db import models
from django.conf import settings
from apps.gigs.choices import *
from talentSite.storage_backends import *
from django.core.exceptions import ValidationError
from uuid import uuid4
from django.db.models.signals import pre_delete
from django.dispatch import receiver


class Category(models.Model):
    name = models.CharField(
        max_length=50)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField()

    class Meta:
        # enforcing that there can not be two categories under a parent with same slug
        unique_together = ('slug', 'parent',)
        verbose_name_plural = "categories"

    def __str__(self):
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return ' -> '.join(full_path[::-1])


class UserImage(models.Model):

    propietary = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def generate_filename(self, filename):
        from apps.profiles.models import UserProfile
        user = UserProfile.objects.get(user=self.propietary)
        url = "%s/userImage/%s" % (str(user.id), filename)
        return url
    image = models.ImageField(
        storage=PublicMediaStorage(file_overwrite=True), upload_to=generate_filename, null=True)
    description = models.CharField(max_length=30, blank=True, null=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.propietary.username + '\'s Image ' + str(self.id)


class UserFile(models.Model):

    def generate_filename(self, filename):
        from apps.profiles.models import UserProfile
        user = UserProfile.objects.get(user=self.propietary)
        url = "%s/files/%s/%s" % (str(user.id), self.url_modifier, filename)
        return url

    propietary = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='propietary')

    isPrivate = models.BooleanField()

    publicFile = models.FileField(
        storage=PublicMediaStorage(), upload_to=generate_filename, null=True)
    privateFile = models.FileField(
        storage=PrivateMediaStorage(), upload_to=generate_filename, null=True)

    description = models.CharField(max_length=30, blank=True, null=True)
    # This helps to prevent name colisions.
    url_modifier = models.TextField(max_length=255, null=False)

    fileExtension = models.TextField(max_length=255, null=False)

    sharedWith = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='sharedWith')

    visible = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.propietary.username + '\'s File ' + str(self.id)

    def get_html_item(self):
        if str.lower(self.fileExtension) == 'png' or str.lower(self.fileExtension) == 'jpeg' or str.lower(self.fileExtension) == 'jpg' or str.lower(self.fileExtension) == 'gif':
            if self.isPrivate:
                return '<img class="object-cover w-full h-full" src="https://hiiwork.s3.amazonaws.com/media/public/%s" alt="%s">' % (self.privateFile, self.privateFile.name.split('/')[-1])
            else:
                return '<img class="object-cover w-full h-full" src="https://hiiwork.s3.amazonaws.com/media/public/%s" alt="%s">' % (self.publicFile, self.publicFile.name.split('/')[-1])
        elif str.lower(self.fileExtension) == 'mp4' or str.lower(self.fileExtension) == 'm4v':
            if self.isPrivate:
                return'<video id="player%s" playsinline controls> <source src="https://hiiwork.s3.amazonaws.com/media/public/%s" type="video/mp4" />  </video> <script> const player%s = new Plyr(document.getElementById("player%s"),{ controls:["play-large", "play", "progress","volume", "mute", "pip", "airplay", "fullscreen"] }); </script>' % (self.privateFile.name.split('/')[-1], self.privateFile, self.privateFile.name.split('/')[-1].split('.')[0], self.privateFile.name.split('/')[-1])
            else:
                return'<video id="player%s" playsinline controls> <source src="https://hiiwork.s3.amazonaws.com/media/public/%s" type="video/mp4" />  </video> <script> const player%s = new Plyr(document.getElementById("player%s"),{ controls:["play-large", "play", "progress","volume", "mute", "pip", "airplay", "fullscreen"] }); </script>' % (self.publicFile.name.split('/')[-1], self.publicFile, self.publicFile.name.split('/')[-1].split('.')[0], self.publicFile.name.split('/')[-1])
        elif str.lower(self.fileExtension) == 'mp3' or str.lower(self.fileExtension) == 'wav':
            if self.isPrivate:
                return'<audio id="player%s" controls> <source src="https://hiiwork.s3.amazonaws.com/media/public/%s" type="audio/mp3"/>  </audio> <script> const player%s = new Plyr(document.getElementById("player%s")); </script>' % (self.privateFile.name.split('/')[-1], self.privateFile, self.privateFile.name.split('/')[-1].split('.')[0], self.privateFile.name.split('/')[-1])
            else:
                return'<audio id="player%s" controls> <source src="https://hiiwork.s3.amazonaws.com/media/public/%s" type="audio/mp3"/>  </audio> <script> const player%s = new Plyr(document.getElementById("player%s")); </script>' % (self.publicFile.name.split('/')[-1], self.publicFile, self.publicFile.name.split('/')[-1].split('.')[0], self.publicFile.name.split('/')[-1])
        elif str.lower(self.fileExtension) == 'pdf':
            if self.isPrivate:
                return '<div class="flex flex-col"> <svg class="w-full h-full p-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12.819 14.427c.064.267.077.679-.021.948-.128.351-.381.528-.754.528h-.637v-2.12h.496c.474 0 .803.173.916.644zm3.091-8.65c2.047-.479 4.805.279 6.09 1.179-1.494-1.997-5.23-5.708-7.432-6.882 1.157 1.168 1.563 4.235 1.342 5.703zm-7.457 7.955h-.546v.943h.546c.235 0 .467-.027.576-.227.067-.123.067-.366 0-.489-.109-.198-.341-.227-.576-.227zm13.547-2.732v13h-20v-24h8.409c4.858 0 3.334 8 3.334 8 3.011-.745 8.257-.42 8.257 3zm-12.108 2.761c-.16-.484-.606-.761-1.224-.761h-1.668v3.686h.907v-1.277h.761c.619 0 1.064-.277 1.224-.763.094-.292.094-.597 0-.885zm3.407-.303c-.297-.299-.711-.458-1.199-.458h-1.599v3.686h1.599c.537 0 .961-.181 1.262-.535.554-.659.586-2.035-.063-2.693zm3.701-.458h-2.628v3.686h.907v-1.472h1.49v-.732h-1.49v-.698h1.721v-.784z"/></svg><div>%s</div></div>' % self.privateFile.name.split('/')[-1]
            else:
                return '<div class="flex flex-col"> <svg class="w-full h-full p-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12.819 14.427c.064.267.077.679-.021.948-.128.351-.381.528-.754.528h-.637v-2.12h.496c.474 0 .803.173.916.644zm3.091-8.65c2.047-.479 4.805.279 6.09 1.179-1.494-1.997-5.23-5.708-7.432-6.882 1.157 1.168 1.563 4.235 1.342 5.703zm-7.457 7.955h-.546v.943h.546c.235 0 .467-.027.576-.227.067-.123.067-.366 0-.489-.109-.198-.341-.227-.576-.227zm13.547-2.732v13h-20v-24h8.409c4.858 0 3.334 8 3.334 8 3.011-.745 8.257-.42 8.257 3zm-12.108 2.761c-.16-.484-.606-.761-1.224-.761h-1.668v3.686h.907v-1.277h.761c.619 0 1.064-.277 1.224-.763.094-.292.094-.597 0-.885zm3.407-.303c-.297-.299-.711-.458-1.199-.458h-1.599v3.686h1.599c.537 0 .961-.181 1.262-.535.554-.659.586-2.035-.063-2.693zm3.701-.458h-2.628v3.686h.907v-1.472h1.49v-.732h-1.49v-.698h1.721v-.784z"/></svg><div>%s</div></div>' % self.publicFile.name.split('/')[-1]


@receiver(pre_delete, sender=UserFile)
def my_handler(sender, instance, **kwargs):
    instance.publicFile.delete(save=False)
    instance.privateFile.delete(save=False)


class Gig(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ForeignKey(
        Category, on_delete=models.SET_DEFAULT, default=1)
    files = models.ManyToManyField(UserFile)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    isFinished = models.BooleanField(default=False)
    isActive = models.BooleanField(default=False)
    isDeleted = models.BooleanField(default=False)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('details', kwargs={'id': self.pk})

    def __str__(self):
        if not self.isFinished:
            return ('An unfinished gig by %s' % (self.author))
        if self.isDeleted:
            return ('"%s", a gig by %s (DELETED)' % (self.title, self.author))
        if self.isActive:
            return ('"%s", a gig by %s (ACTIVE)' % (self.title, self.author))
        else:
            return ('"%s", a gig by %s (PAUSED)' % (self.title, self.author))


class Feature(models.Model):
    name = models.CharField(max_length=50, blank=False)
    gig = models.ForeignKey(Gig, on_delete=models.CASCADE)
    tier1 = models.BooleanField(default=False)
    tier2 = models.BooleanField(default=False)
    tier3 = models.BooleanField(default=False)

    def __str__(self):
        return ('A feature of %s' % (self.gig))

    def clean(self):
        if not (self.tier1 or self.tier2 or self.tier3):
            raise ValidationError(
                "¡Selecciona al menos un paquete para ésta característica!")

    def is_included_in_tier(self, tier):
        if self.tier1 and tier == 'B':
            return True
        elif self.tier2 and tier == 'N':
            return True
        elif self.tier3 and tier == 'P':
            return True
        else:
            return False


class Requirement(models.Model):
    """The requirements so the freelancer can do the gig."""
    requirement = models.TextField(blank=False, max_length=50)
    description = models.TextField(blank=False, max_length=200)
    gig = models.ForeignKey(Gig, on_delete=models.CASCADE)

    class Meta:
        """Meta definition for Requirement."""
        verbose_name = 'Requirement'
        verbose_name_plural = 'Requirements'

    def __str__(self):
        """Unicode representation of Requirement."""
        return 'Requirement for %s' % self.gig


class Extra(models.Model):
    title = models.CharField(max_length=50, blank=False)
    gig = models.ForeignKey(Gig, on_delete=models.CASCADE)
    description = models.TextField(blank=False, max_length=200)
    price1 = models.IntegerField(choices=PRICE_CHOICES, blank=False)
    price2 = models.IntegerField(choices=PRICE_CHOICES, blank=False)
    price3 = models.IntegerField(choices=PRICE_CHOICES, blank=False)
    extraDays1 = models.IntegerField(blank=False)
    extraDays2 = models.IntegerField(blank=False)
    extraDays3 = models.IntegerField(blank=False)
    numberOfTimesYouCanBuy1 = models.IntegerField(
        choices=POSITIVE_INTEGERS_UP_TO_100, blank=False, null=True)
    numberOfTimesYouCanBuy2 = models.IntegerField(
        choices=POSITIVE_INTEGERS_UP_TO_100, blank=False, null=True)
    numberOfTimesYouCanBuy3 = models.IntegerField(
        choices=POSITIVE_INTEGERS_UP_TO_100, blank=False, null=True)
    isFast = models.BooleanField(default=False, editable=False)

    @classmethod
    def create(cls, isFast):
        extra = cls(isFast=isFast)
        extra.title = 'Entrega Rápida'
        extra.description = 'El freelancer entregará tu orden antes de la fecha original.'
        return extra

    def __str__(self):
        if self.isFast:
            return ('Fast delivery extra for %s' % (self.gig))
        return ('Extra for %s' % (self.gig))

    def get_price_string(self, index):
        if self.isFast:
            return "+ $%d" % self.price1
        elif index == 1:
            return "+ $%d" % self.price1
        elif index == 2:
            return "+ $%d" % self.price2
        elif index == 3:
            return "+ $%d" % self.price3
        else:
            return "Invalid index."

    def get_extraDays_string(self, index):
        if self.isFast:
            string = "- %d" % self.extraDays1
            number = self.extraDays1
        elif index == 1:
            string = "+ %d" % self.extraDays1
            number = self.extraDays1
        elif index == 2:
            string = "+ %d" % self.extraDays2
            number = self.extraDays2
        elif index == 3:
            string = "+ %d" % self.extraDays3
            number = self.extraDays3
        else:
            return "Invalid index."

        if number == 1:
            return string + " día"
        else:
            return string + " días"

    def get_days_for_tier(self, tier):
        if tier == 'B':
            return self.extraDays1
        elif tier == 'N':
            return self.extraDays2
        else:
            return self.extraDays3

    def get_price_for_tier(self, tier):
        if tier == 'B':
            return self.price1
        elif tier == 'N':
            return self.price2
        else:
            return self.price3


class Package(models.Model):
    gig = models.ForeignKey(Gig, on_delete=models.CASCADE)
    tier = models.CharField(max_length=1)
    description = models.CharField(max_length=255, blank=False)
    deliveryTime = models.IntegerField(
        choices=DELIVERY_TIME_CHOICES, blank=False)
    revisions = models.IntegerField(choices=REVISION_CHOICES, blank=False)
    price = models.IntegerField(choices=PRICE_CHOICES, blank=False)
    features = models.ManyToManyField(Feature)

    @classmethod
    def create(cls, tier):
        package = cls(tier=tier)
        return package

    def get_package_tier(self):
        if self.tier == 'B':
            return ('Paquete Básico')
        elif self.tier == 'N':
            return ('Paquete Normal')
        else:
            return ('Paquete Pro')

    def __str__(self):
        if self.tier == 'B':
            return ('Basic Package for %s' % (self.gig))
        elif self.tier == 'N':
            return ('Normal Package for %s' % (self.gig))
        elif self.tier == 'P':
            return ('Pro Package for %s' % (self.gig))
        else:
            return ('Package has no Gig %s' % (self.gig))


class FAQ(models.Model):
    gig = models.ForeignKey(Gig, on_delete=models.CASCADE)
    question = models.TextField(blank=False, max_length=100)
    answer = models.TextField(blank=False)

    def __str__(self):
        return self.question


class Order(models.Model):

    """Model definition for Order."""
    orderID = models.UUIDField(
        default=uuid4, unique=True, db_index=True, editable=False, primary_key=True)
    orderString = models.TextField()
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='buyer')
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='seller')
    payed = models.BooleanField(default=False)
    price = models.IntegerField()
    feePercentage = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta definition for Order."""

        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        """Unicode representation of Order."""
        return 'ID: ' + str(self.orderID) + ' by ' + str(self.buyer)

    def get_order_details(self):
        from apps.gigs.utils import PackageCalculator, OrderDecoder
        return OrderDecoder.decode(self.orderString)

    def get_delivery_date(self):
        from apps.gigs.utils import PackageCalculator, OrderDecoder
        orderDetails = self.get_order_details()
        return PackageCalculator.getDeliveryDate(orderDetails['package'], orderDetails['selectedExtras'])

    def get_gig_author(self):
        from apps.profiles.models import UserProfile
        author = UserProfile.objects.get(
            user=self.get_order_details()['package'].gig.author)
        return author

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('req', kwargs={'orderID': self.orderID})

    def get_status(self):
        from django.urls import reverse
        return reverse('req', kwargs={'orderID': self.orderID})


class Review(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    calification = models.IntegerField(choices=RATING_CHOICES, blank=False)
    comment = models.TextField(blank=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.calification)


class RequirementClient(models.Model):
    """Model definition for RequirementClient."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE)

    files = models.ManyToManyField(UserFile)

    comments = models.TextField(null=True)
    delivered = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta definition for RequirementClient."""

        verbose_name = 'RequirementClient'
        verbose_name_plural = 'RequirementClients'

    def __str__(self):
        """Unicode representation of RequirementClient."""
        return "A requirement"
