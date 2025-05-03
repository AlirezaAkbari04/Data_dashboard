from django.db import models
from django.contrib.auth.models import User
from data_manager.models import Dataset

class ChatSession(models.Model):
    """"Tracks conversations with the LLM about data"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat about {self.dataset.name}"
