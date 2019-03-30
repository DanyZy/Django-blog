from django.contrib import admin
from .models import Post


class PostModelAdmin(admin.ModelAdmin):
    class Meta:
        model = Post


admin.site.register(Post)
