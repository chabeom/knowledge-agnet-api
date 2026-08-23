from django.db import models


class Document(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    source = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.title
