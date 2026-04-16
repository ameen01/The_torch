from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Category, ReadingModule, UserVocabulary, ListingModule, WritingProject, ActivitySession, UserStats ,Vocabulary

# --- Inlines allow you to edit related items on the same page ---




# Also, add it as an inline to Category if you want to add words while creating a category
class VocabularyInline(admin.TabularInline):
    model = Vocabulary
    extra = 3

class UserVocabularyInline(admin.TabularInline):
    model = UserVocabulary
    extra = 1 # Shows one blank row for adding new words

class ReadingModuleInline(admin.StackedInline):
    model = ReadingModule
    extra = 0

class ListingModuleInline(admin.StackedInline):
    model = ListingModule
    extra = 0

# --- Main Admin Classes ---
@admin.register(Vocabulary)
class VocabularyAdmin(admin.ModelAdmin):
    list_display = ('word', 'category','image','audio')
    list_filter = ('category',)
    search_fields = ('word',)
    
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_name')
    inlines = [ReadingModuleInline, ListingModuleInline,VocabularyInline]

@admin.register(ReadingModule)
class ReadingAdmin(admin.ModelAdmin):
    list_display = ('title', 'category' ,'slug')
    list_filter = ('category',)
    prepopulated_fields = {'slug': ('title',)} #
    inlines = [UserVocabularyInline]

@admin.register(ListingModule)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'category','audio','slug',)
    search_fields = ('title', 'audio')

@admin.register(ActivitySession)
class ActivitySessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'duration_seconds', 'start_time')
    readonly_fields = ('start_time',) # Prevent manual editing of session starts

# Register remaining models
admin.site.register(WritingProject)
admin.site.register(UserStats)
admin.site.register(UserVocabulary)