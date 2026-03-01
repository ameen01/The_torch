from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


#fix it so every model have its on category 

# --- 1. CATEGORIZATION ---
class Category(models.Model):
    """Examples: Food, Animals, Furniture, Technology"""
    name = models.CharField(max_length=100, unique=True)
    icon_name = models.CharField(max_length=50, help_text="FontAwesome icon name (e.g., fa-utensils)")

    def __str__(self):
        return self.name

# --- 2. THE ACTIVITY MODULES ---


#add icon for all the models category
class ReadingModule(models.Model):
    """Reading content with optional vocabulary words for the user."""
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200)
    story_content = models.TextField()
    slug = models.SlugField(max_length=250, unique=True, blank=True) # New Field
    # Automatically generate the slug from the title on save
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Reading: {self.title}"

class UserVocabulary(models.Model):
    """Words the user adds manually to their 'Reading' library."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reading_module = models.ForeignKey(ReadingModule, on_delete=models.CASCADE, related_name="user_words")
    word = models.CharField(max_length=100)
    definition = models.TextField(blank=True)

class Vocabulary(models.Model):
    """Vocabulary of Words"""
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    word = models.CharField(max_length=100)
    icon_name = models.CharField(max_length=50,db_default= 'fa-solid fa-building-circle-xmark', help_text="FontAwesome icon name (e.g., fa-utensils)")
    definition = models.TextField(blank=True)
    def __str__(self):
        return f"Vocabulary {self.word}"

class ListingModule(models.Model):
    """Listing tasks that utilize AI voice/Audio reading."""
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200)
    # This text will be sent to the AI Voice API
    text_for_audio = models.TextField(help_text="The text the AI will read to the user")
    correct_list_items = models.TextField(help_text="Comma-separated list of items the user must identify")
    slug = models.SlugField(max_length=250, unique=True, blank=True) # New Field
    # Automatically generate the slug from the title on save
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Listing: {self.title}"



class WritingProject(models.Model):
    """Advanced writing projects (Drafts)."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Writing: {self.title} by {self.user.username}"

# --- 3. TRACKING & ANALYTICS (The 'Missing' Piece) ---

class ActivitySession(models.Model):
    """Tracks what the user did last and for how long."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Polymorphic-style link (links to whichever module they were using)
    activity_type = models.CharField(max_length=50, choices=[
        ('reading', 'Reading'),
        ('listing', 'Listing'),
        ('writing', 'Writing')
    ])
    activity_id = models.PositiveIntegerField() # Stores the ID of the specific Reading/Listing/Writing module
    
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(default=0) # Calculated on save
    
    last_position = models.TextField(blank=True, help_text="Stores scroll position or last word typed")

    def __str__(self):
        return f"{self.user.username} - {self.activity_type} session"

class UserStats(models.Model):
    """Global aggregate for the dashboard icons."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_study_time = models.PositiveIntegerField(default=0) # In minutes
    last_activity_date = models.DateTimeField(auto_now=True)