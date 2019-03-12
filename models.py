from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.gis.db.models import PointField
from django.contrib.gis.geos import Point

from geopy import geocoders
from localflavor.us.models import USStateField
from phonenumber_field.modelfields import PhoneNumberField


class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
	hometown = models.CharField(max_length=30, blank=True, help_text="Where the user came from.")
	joined = models.DateField(auto_now_add=True, help_text="Date the user joined.")
	last_change = models.DateField(auto_now=True, help_text="Date the user data was last changed.")
	organization = models.ForeignKey('Organization', related_name='profile_organization', on_delete=models.SET_NULL, blank=True, null=True, default=1)
	todo = models.ManyToManyField('Item', through='Todo', related_name='profile_todo')
	bookmarks = models.ManyToManyField('Item', through='Bookmark', related_name='profile_bookmarks')
	location = PointField(blank=True, null=True)

	def __str__(self):
		return self.user.email

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
	instance.profile.save()


class Metro(models.Model):
	name = models.CharField(max_length=128, unique=True)

	def __str__(self):
		return self.name


class Organization(models.Model):
	name = models.CharField(max_length=128, unique=True)
	metro = models.ForeignKey('Metro', related_name='organization_metro', on_delete=models.SET_DEFAULT, default=1, help_text="The Metro Area this Organization is located in, to share items.")
	public = models.BooleanField(default=True)
	default_items = models.ManyToManyField('Item', through='Default', related_name='organization_default_items', blank=True, help_text="Default Items for new user.")
	discover_items = models.ManyToManyField('Item', through='Discover', related_name='organization_discover_items', blank=True, help_text="Items to show under 'Discover'.")
	tips = models.ManyToManyField('Tip', blank=True, help_text="Tips to display")
	nav_image = models.ImageField(blank=True)
	nav_name = models.CharField(max_length=128, blank=True)
	categories = models.ManyToManyField('Category', through='OrgCategory', related_name='organization_categories', blank=True, help_text="Categories to show on the search screen.")
	link = models.URLField(blank=True, help_text="URL for Nav site")
	location = PointField(blank=True, null=True)

	def __str__(self):
		return self.name


class ProspectiveUser(models.Model):
	email = models.EmailField(unique=True)
	organization = models.ForeignKey('Organization', on_delete=models.CASCADE)
	
	def __str__(self):
		return self.email


class Tip(models.Model):
	name = models.CharField(max_length=128, help_text="Tip headline")
	content = models.TextField(help_text="Tip text")
	# keep track of whether seen by user or not?
	
	def __str__(self):
		return self.name


class Item(models.Model):
	name = models.CharField(max_length=128, help_text="Title")
	content = models.TextField(blank=True, help_text="Description")
	public = models.BooleanField(default=False, help_text="Is this publicly shown?")
	sponsor = models.CharField(max_length=128, blank=True, help_text="Name of sponsor, if sponsored.")
	link = models.URLField(blank=True, help_text="Website URL")
	image = models.ImageField(blank=True) # use thumbnail field for image?
	ctas = models.ManyToManyField('Cta', blank=True, help_text="Call To Action Buttons to be displayed.")
	next = models.ManyToManyField('Item', related_name='next_items', symmetrical=False, blank=True, limit_choices_to={'place': None}, help_text="Items to be added to User's list when this item is completed.")
	notes = models.TextField(blank=True, help_text="For internal use only, will not be shown")
	tags = models.ManyToManyField('Tag', blank=True)
	deadline = models.DateTimeField(blank=True, null=True)
	video = models.FileField(blank=True) # do we need to post-process this video in any way?

	def __str__(self):
		return self.name


class Group(Item):
	items = models.ManyToManyField('Item', related_name='group_items', symmetrical=False, help_text="Items in this group.")


class Place(Item):
	metro = models.ManyToManyField('Metro', related_name='place_metro', blank=True, help_text="Metro areas that contain this place.")
	address = models.CharField(max_length=128, help_text="Street Address")
	city = models.CharField(max_length=128)
	state = USStateField()
	location = PointField(blank=True, null=True)
	phone = PhoneNumberField(blank=True, verbose_name="Phone Number")
	featured = models.BooleanField(default=False, help_text="Does this place show up as featured in search results?")
	category = models.ManyToManyField('Category', blank=True, help_text="Categories that this place appears under in search results.")
	ratings = models.ManyToManyField('Profile', through='Rating', blank=True)

	def rating(self):
		return Rating.objects.filter(place=self).aggregate(models.Avg('rating'))
	
	def save(self, *args, **kwargs):
		if self.address:
			fulladdress = self.address + ", " + self.city + ", " + self.state
			if not self.location:
				try:
					g = geocoders.GoogleV3()
					l = g.geocode(fulladdress)
					self.location = Point(l.latitude, l.longitude)
				except:
					print("geocoding error")
		super(Place, self).save(*args, **kwargs)


class Category(models.Model):
	name = models.CharField(max_length=128, unique=True)
	image = models.ImageField(blank=True)
	tags = models.ManyToManyField('Tag', blank=True, help_text="Tags that we offer the user when searching within this Category.")

	def __str__(self):
		return self.name

	class Meta:
		verbose_name_plural = "categories"


class Tag(models.Model):
	name = models.CharField(max_length=128, unique=True)

	def __str__(self):
		return self.name


class Cta(models.Model):
	name = models.CharField(max_length=128, help_text="CTA Button text")
	link = models.URLField(help_text="Website URL that clicking this CTA button goes to.")

	def __str__(self):
		return self.name


class Rating(models.Model):
	profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
	place = models.ForeignKey('Place', on_delete=models.CASCADE)
	rating = models.IntegerField(help_text="Number of stars from 1-5.")
	# need to add unique constraints to prevent multiple ratings from the same user?


class Todo(models.Model):
	profile = models.ForeignKey('Profile', related_name='todo_profile', on_delete=models.CASCADE)
	item = models.ForeignKey('Item', related_name='todo_item', on_delete=models.CASCADE)
	order = models.IntegerField() # required?
	done = models.BooleanField(default=False)
	# need to add unique constraints to prevent duplicate todo items?
	
	class Meta:
		verbose_name = "todo item"
		ordering = ('order',)


class Bookmark(models.Model):
	profile = models.ForeignKey('Profile', related_name='bookmark_profile', on_delete=models.CASCADE)
	item = models.ForeignKey('Item', related_name='bookmark_item', on_delete=models.CASCADE)
	datetime = models.DateTimeField(auto_now_add=True)
	# need to add unique constraints to prevent duplicate bookmarks?

	class Meta:
		verbose_name = "bookmark item"
		ordering = ('datetime',)


class Discover(models.Model):
	organization = models.ForeignKey('Organization', related_name='discover_organization', on_delete=models.CASCADE, blank=True, null=True)
	item = models.ForeignKey('Item', related_name='discover_item', on_delete=models.CASCADE)
	order = models.IntegerField(blank=True, null=True)
	
	class Meta:
		verbose_name = "discover item"
		ordering = ('order',)


class Default(models.Model):
	organization = models.ForeignKey('Organization', related_name='default_organization', on_delete=models.CASCADE, blank=True, null=True)
	item = models.ForeignKey('Item', related_name='default_item', on_delete=models.CASCADE)
	order = models.IntegerField(blank=True, null=True) # should this be required?
	
	class Meta:
		verbose_name = "default item"
		ordering = ('order',)


class OrgCategory(models.Model):
	organization = models.ForeignKey('Organization', related_name='category_organization', on_delete=models.CASCADE, blank=True, null=True)
	category = models.ForeignKey('Category', related_name='organization_category', on_delete=models.CASCADE)
	order = models.IntegerField(blank=True, null=True)
	
	class Meta:
		verbose_name = "category"
		ordering = ('order',)

