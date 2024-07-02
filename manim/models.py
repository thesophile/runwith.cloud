from django.db import models

class User(models.Model):
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.username

class Code(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='codes')
    code_text = models.TextField()

    def __str__(self):
        return f"Code for {self.user.username}"

