from django.contrib import admin

from posts.models import Post

class PostModelAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "slug",
        "title",
        "updated",
        "timestamp",
        "image"
    ]
    list_display_links = ["id"]
    list_filter = ["updated", "timestamp"]
    search_fields = ["title", "content"]
    class Meta:
        model = Post

admin.site.register(Post, PostModelAdmin)
