from django.db import models
from django.utils import timezone

class Feedback(models.Model):
    """
    Main feedback model - stores user feedback
    Simple design: content, username, timestamp
    """
    content = models.TextField(help_text="The feedback content")
    username = models.CharField(max_length=50, help_text="Who posted this feedback")
    created_at = models.DateTimeField(default=timezone.now, help_text="When feedback was created")
    
    class Meta:
        ordering = ['-created_at']  # Latest first
    
    def __str__(self):
        return f"{self.username}: {self.content[:50]}..."
    
    def get_upvote_count(self):
        """Count total upvotes for this feedback"""
        return self.upvotes.count()
    
    def user_has_voted(self, username):
        """Check if specific user has upvoted this feedback"""
        return self.upvotes.filter(username=username).exists()

class Upvote(models.Model):
    """
    Upvote model - tracks who voted for what
    One vote per user per feedback (case sensitive username)
    """
    feedback = models.ForeignKey(
        Feedback, 
        on_delete=models.CASCADE, 
        related_name='upvotes'
    )
    username = models.CharField(max_length=50, help_text="Who voted")
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        # Prevent duplicate votes from same user
        unique_together = ('feedback', 'username')
    
    def __str__(self):
        return f"{self.username} upvoted: {self.feedback.content[:30]}..."
