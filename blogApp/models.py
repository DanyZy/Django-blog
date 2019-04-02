from django.db import models
from django.utils import timezone


def upload_location(instance, filename):
    return "%s/%s" %(instance.id, filename)


class Post(models.Model):
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()
    image = models.ImageField(upload_to=upload_location,
                              null=True,
                              blank=True,
                              height_field='height_field',
                              width_field='width_field')
    height_field = models.IntegerField(default=0)
    width_field = models.IntegerField(default=0)
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.title

    def get_excerpt_text(self):
        return self.text[:90] + "..." if len(self.text) > 90 else self.text

    def get_excerpt_title(self):
        return self.title[:10] + "..." if len(self.title) > 10 else self.title
