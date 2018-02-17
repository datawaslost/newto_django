from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from localflavor.us.models import USStateField
from phonenumber_field.modelfields import PhoneNumberField


class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	hometown = models.CharField(max_length=30, blank=True)
	joined = models.DateField(auto_now_add=True)
	last_change = models.DateField(auto_now=True)
	metro = models.ForeignKey('Metro', related_name='profile_metro', on_delete=models.SET_NULL, blank=True, null=True)
	school = models.ForeignKey('School', related_name='profile_school', on_delete=models.SET_NULL, blank=True, null=True)
	todo = models.ManyToManyField('Item', through='Todo', related_name='profile_todo')
	bookmarks = models.ManyToManyField('Item', through='Bookmark', related_name='profile_bookmarks')

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
	instance.profile.save()


class Metro(models.Model):
	name = models.CharField(max_length=128, unique=True)
	public = models.BooleanField(default=True)
	default_items = models.ManyToManyField('Item', related_name='metro_default_items', blank=True)
	discover_items = models.ManyToManyField('Item', related_name='metro_discover_items', blank=True)
	tips = models.ManyToManyField('Tip', blank=True)
	# need a through modeal to organize tips or default/discover items?


class School(Metro):
	metro = models.ForeignKey('Metro', related_name='school_metro', on_delete=models.SET_NULL, blank=True, null=True)


class ProspectiveUser(models.Model):
	email = models.EmailField(unique=True)
	school = models.ForeignKey('School', on_delete=models.CASCADE)


class Tip(models.Model):
	name = models.CharField(max_length=128)
	content = models.TextField()
	# keep track of whether seen by user or not?


class Item(models.Model):
	name = models.CharField(max_length=128)
	content = models.TextField()
	public = models.BooleanField(default=False)
	sponsor = models.CharField(max_length=128)
	link = models.URLField()
	image = models.ImageField()
	# use thumbnail field for image?
	ctas = models.ManyToManyField('Cta', blank=True)

	def __str__(self):
		return self.name


class Group(Item):
	items = models.ManyToManyField('Item', related_name='group_items', symmetrical=False)


class Place(Item):
	metro = models.ForeignKey('Metro', on_delete=models.SET_NULL, blank=True, null=True)
	address = models.CharField(max_length=128)
	city = models.CharField(max_length=128)
	state = USStateField()
	# need zip?
	# hours = models.CharField(max_length=128)
	# need more complex hours field, currently using openinghours
	phone = PhoneNumberField(blank=True)
	featured = models.BooleanField(default=False)
	category = models.ForeignKey('Category', on_delete=models.SET_NULL, blank=True, null=True)
	tags = models.ManyToManyField('Tag', blank=True)
	ratings = models.ManyToManyField('Profile', through='Rating', blank=True)


class Category(models.Model):
	name = models.CharField(max_length=128, unique=True)
	image = models.ImageField()
	tags = models.ManyToManyField('Tag', blank=True)


class Tag(models.Model):
	name = models.CharField(max_length=128, unique=True)


class Cta(models.Model):
	name = models.CharField(max_length=128)
	link = models.URLField()


class Rating(models.Model):
	profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
	place = models.ForeignKey('Place', on_delete=models.CASCADE)
	rating = models.IntegerField()
	# need to add unique constraints to prevent multiple ratings from the same user?


class Todo(models.Model):
	profile = models.ForeignKey('Profile', related_name='todo_profile', on_delete=models.CASCADE)
	item = models.ForeignKey('Item', related_name='todo_item', on_delete=models.CASCADE)
	order = models.IntegerField()
	done = models.BooleanField(default=False)
	# need to add unique constraints to prevent duplicate items?


class Bookmark(models.Model):
	profile = models.ForeignKey('Profile', related_name='bookmark_profile', on_delete=models.CASCADE)
	item = models.ForeignKey('Item', related_name='bookmark_item', on_delete=models.CASCADE)
	datetime = models.DateTimeField(auto_now_add=True)
	# need to add unique constraints to prevent duplicate items?
