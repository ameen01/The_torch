
from django.utils import timezone
from django.contrib import messages

from django.shortcuts import render, get_object_or_404, redirect
from .models import Vocabulary, Category, ListingModule, ReadingModule, WritingProject, ActivitySession, UserProfile, UserVocabulary
from django.db.models import Sum
from django.http import JsonResponse
import requests
import json
import os
from gtts import gTTS
from .localllm import generate_vocabulary_list, get_vocabulary_details
from django.core.files import File
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, LoginForm
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
import xml.etree.ElementTree as ET
import re

# Create your views here.
def index(request):
    return render(request, 'LangLens/index.html')



def home(request):
    return render(request, 'LangLens/index.html')


def local_news(request):
    # Feed source: Winnipeg Free Press Manitoba local news RSS
    feed_url = 'https://www.winnipegfreepress.com/rss/'
    articles = []
    now = datetime.now(tz=timezone.UTC)
    since = now - timedelta(hours=24)

    try:
        response = requests.get(feed_url, timeout=15)
        response.raise_for_status()
        root = ET.fromstring(response.content)

        for item in root.findall('.//item'):
            title = item.findtext('title', '').strip()
            link = item.findtext('link', '').strip()
            description = item.findtext('description', '').strip()
            pub_date_text = item.findtext('pubDate') or item.findtext('published')

            # Extract image from description if available
            image_url = None
            if '<img' in description:
                img_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
                matches = re.findall(img_pattern, description)
                if matches:
                    image_url = matches[0]  # Take the first image

            # Clean description by removing img tags
            clean_description = re.sub(r'<img[^>]+>', '', description).strip()

            published = None
            if pub_date_text:
                try:
                    published = parsedate_to_datetime(pub_date_text)
                    if published.tzinfo is None:
                        published = published.replace(tzinfo=timezone.UTC)
                except Exception:
                    published = None

            if not published or published < since:
                continue

            articles.append({
                'title': title,
                'link': link,
                'description': clean_description,
                'image_url': image_url,
                'published': published,
            })

        articles.sort(key=lambda a: a['published'], reverse=True)
    except Exception as e:
        articles = []
        print('Local news feed error:', e)

    return render(request, 'LangLens/local_news.html', {
        'articles': articles,
        'feed_source': 'Winnipeg Free Press',
        'country': 'Canada',
        'province': 'Manitoba',
    })


def sign_in(request):
    error = ''
    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.cleaned_data.get('user')
            login(request, user)
            return redirect('index')
        else:
            error = form.non_field_errors() or ''
            messages.error(request, error)

    return render(request, 'LangLens/login.html', {
        'form': form,
        'error': error,
    })


def resgitor(request):
    message = ''
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create default UserProfile for new user
            UserProfile.objects.create(
                user=user,
                bio='',
                location='',
                website='',
            )
            message = 'Registration successful. You can now log in.'
            messages.success(request, message)
            return redirect('login')
        else:
            # will display errors in template
            pass
    else:
        form = RegistrationForm()

    return render(request, 'LangLens/signup.html', {
        'form': form,
        'message': message,
    })


def  reading_category_list(request):
    filter_names = ['News', 'Emails', 'Short stories']
    categories = Category.objects.filter(name__in=filter_names)
    return render(request, 'LangLens/reading_category.html',{'categories': categories})


def reading_article_list(request,category_id):
    category = get_object_or_404(Category, pk=category_id)
    categories = ReadingModule.objects.filter(category=category)
    return render(request, 'LangLens/reading_list.html',{'categories': categories, 'category':category})


def reading_detail(request, slug):
    text = get_object_or_404(ReadingModule, slug=slug)
    templates = {
        'Emails': 'LangLens/reading_email.html',
        'Short stories': 'LangLens/reading_stories.html',
        'News': 'LangLens/reading_news.html',
    }
    
    # Track activity session if user is authenticated
    if request.user.is_authenticated:
        ActivitySession.objects.create(
            user=request.user,
            activity_type='reading',
            activity_id=text.id,
            last_position=text.title[:100]
        )
    
    # Get the template from the dictionary, default to news if not found
    template_path = templates.get(text.category.name, 'LangLens/reading_news.html')
    return render(request, template_path, {'text': text})


def get_vocbulary_categories(request):
    excluded_category = ['News', 'Emails', 'Short stories']
    categories = Category.objects.exclude(name__in=excluded_category)
    return render(request, 'LangLens/vocabulary_category.html', {'categories':categories})


def display_vocabulary_list(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    vocabularies = Vocabulary.objects.filter(category=category)
    for v in vocabularies:
        print(v.audio)
    
    # Track activity session if user is authenticated
    if request.user.is_authenticated:
        ActivitySession.objects.create(
            user=request.user,
            activity_type='vocabulary',
            activity_id=category_id,
            last_position=f"Category: {category.name}"
        )
    
    return render(request, 'LangLens/vocabulary.html',{'category': category, 'vocabularies': vocabularies})


def listening_category_list(request):
    filter_names = ['News', 'Emails', 'Short stories']
    categories = Category.objects.filter(name__in=filter_names)
    return render(request,'LangLens/listening_list.html',{'categories': categories,})

def listening_audio_list(requset, category_id):
    category = get_object_or_404(Category, pk=category_id)
    categories = ListingModule.objects.filter(category=category)
    return render(requset, 'LangLens/listening_audio_list.html',{'categories':categories, 'category':category})


def listening_detail(request, slug):
    text = get_object_or_404(ListingModule, slug=slug)
    templates = {
        'Emails': 'LangLens/listening_email.html',
        'Short stories': 'LangLens/listening_stories.html',
        'News': 'LangLens/listening_news.html',
    }
    
    # Track activity session if user is authenticated
    if request.user.is_authenticated:
        ActivitySession.objects.create(
            user=request.user,
            activity_type='listening',
            activity_id=text.id,
            last_position=text.title[:100]
        )
    
    # Get the template from the dictionary, default to news if not found
    template_path = templates.get(text.category.name, 'LangLens/listening_stories.html')
    return render(request, template_path, {'text': text})


@login_required(login_url='login')
def writing(request):
    user = request.user
    project = None
    message = ''
    error = ''

    writing_session = None
    if request.session.get('writing_session_id'):
        try:
            writing_session = ActivitySession.objects.get(
                id=request.session.get('writing_session_id'), user=user, activity_type='writing'
            )
        except ActivitySession.DoesNotExist:
            writing_session = None

    if not writing_session:
        writing_session = ActivitySession.objects.create(user=user, activity_type='writing', activity_id=0, last_position='')
        request.session['writing_session_id'] = writing_session.id

    if request.method == 'POST':
        project_id = request.POST.get('project_id')
        action = request.POST.get('action', 'save')
        title = request.POST.get('title', '').strip() or 'Untitled Project'
        content = request.POST.get('content', '').strip()
        status = request.POST.get('status', 'draft')
        word_goal = request.POST.get('word_goal', '500')
        due_date = request.POST.get('due_date', '')

        try:
            word_goal = int(word_goal)
            if word_goal <= 0:
                word_goal = 500
        except Exception:
            word_goal = 500

        if action == 'delete':
            if not project_id:
                error = 'Select a saved note to delete.'
            else:
                project = get_object_or_404(WritingProject, id=project_id, user=user)
                project.delete()
                message = 'Note deleted successfully.'
                project = None
        else:
            if not content:
                error = 'Content cannot be empty. Please type some text to save.'
            else:
                if project_id:
                    project = get_object_or_404(WritingProject, id=project_id, user=user)
                    project.title = title
                    project.content = content
                    project.status = status
                    project.word_goal = word_goal
                    if due_date:
                        try:
                            from datetime import datetime
                            project.due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
                        except Exception:
                            project.due_date = None
                    project.save()
                    message = 'Updated successfully.'
                else:
                    project = WritingProject.objects.create(
                        user=user,
                        title=title,
                        content=content,
                        status=status,
                        word_goal=word_goal,
                        due_date=due_date or None,
                    )
                    message = 'Saved successfully.'

        if writing_session:
            writing_session.end_time = timezone.now()
            writing_session.duration_seconds = int((writing_session.end_time - writing_session.start_time).total_seconds())
            writing_session.last_position = content[:1000]
            writing_session.activity_id = project.id if project else (writing_session.activity_id or 0)
            writing_session.save()
            request.session.pop('writing_session_id', None)

        if action == 'autosave':
            return JsonResponse({
                'status': 'ok' if not error else 'error',
                'message': message or error,
                'project_id': project.id if project else None,
            }, status=200 if not error else 400)

    elif request.method == 'GET':
        load_id = request.GET.get('project_id')
        if load_id:
            project = get_object_or_404(WritingProject, id=load_id, user=user)
            if writing_session:
                writing_session.activity_id = project.id
                writing_session.save()

    recent_projects = WritingProject.objects.filter(user=user).order_by('-updated_at')[:5]

    return render(request, 'LangLens/writing.html', {
        'project': project,
        'recent_projects': recent_projects,
        'message': message,
        'error': error,
    })


@login_required(login_url='login')
def dashboard(request):
    user = request.user

    totals = ActivitySession.objects.filter(user=user).values('activity_type').annotate(total_seconds=Sum('duration_seconds'))
    activity_map = {'reading': 0, 'listing': 0, 'vocabulary': 0, 'writing': 0}
    for entry in totals:
        activity_map[entry['activity_type']] = entry['total_seconds'] or 0

    def fmt(sec):
        if not sec:
            return '0m'
        h = sec // 3600
        m = (sec % 3600) // 60
        s = sec % 60
        if h:
            return f"{h}h {m}m"
        if m:
            return f"{m}m {s}s"
        return f"{s}s"

    reading_time = fmt(activity_map.get('reading', 0))
    listening_time = fmt(activity_map.get('listening', 0))
    vocabulary_time = fmt(activity_map.get('vocabulary', 0))
    writing_time = fmt(activity_map.get('writing', 0))

    writing_projects_count = WritingProject.objects.filter(user=user).count()
    reading_modules_count = ReadingModule.objects.count()
    vocabulary_count = Vocabulary.objects.count()
    listening_modules_count = ListingModule.objects.count()
    
    # Get recent activity sessions
    recent_activities = ActivitySession.objects.filter(user=user).order_by('-start_time')[:8]

    active_project = WritingProject.objects.filter(user=user).order_by('-updated_at').first()
    if active_project:
        active_title = active_project.title or 'Untitled Project'
        active_content = active_project.content or ''
        active_words = len(active_content.strip().split()) if active_content.strip() else 0
        active_target = 2500
        active_progress = min(100, int((active_words / active_target) * 100)) if active_target > 0 else 0
        active_due = 'No deadline set'
    else:
        active_title = 'No active project yet'
        active_content = 'Create a new writing project to kickstart your workflow.'
        active_words = 0
        active_target = 2500
        active_progress = 0
        active_due = 'Not set'

    total_time = fmt(sum(activity_map.values()))

    recent_projects = WritingProject.objects.filter(user=user).order_by('-updated_at')[:5]

    return render(request, 'LangLens/dashboard.html', {
        'reading_time': reading_time,
        'listening_time': listening_time,
        'vocabulary_time': vocabulary_time,
        'writing_time': writing_time,
        'writing_projects_count': writing_projects_count,
        'reading_modules_count': reading_modules_count,
        'vocabulary_count': vocabulary_count,
        'listening_modules_count': listening_modules_count,
        'total_time': total_time,
        'active_project_title': active_title,
        'active_project_type': 'Writing',
        'active_project_words': active_words,
        'active_project_target': active_target,
        'active_project_progress': active_progress,
        'active_project_due': active_due,
        'active_project_id': active_project.id if active_project else None,
        'weekly_engagement': 75,
        'recent_projects': recent_projects,
        'recent_activities': recent_activities,
    })


@login_required(login_url='login')
def profile_edit(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        # Update User model fields
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.email = request.POST.get('email', '').strip()
        user.save()
        
        # Update UserProfile fields
        profile.bio = request.POST.get('bio', '').strip()
        profile.location = request.POST.get('location', '').strip()
        profile.website = request.POST.get('website', '').strip()
        
        # Handle date of birth
        date_of_birth = request.POST.get('date_of_birth', '').strip()
        if date_of_birth:
            try:
                from datetime import datetime
                profile.date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
            except ValueError:
                pass  # Keep existing value if invalid
        
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile_edit')
    
    return render(request, 'LangLens/profile_edit.html', {
        'user': user,
    })


@login_required(login_url='login')
def my_vocabularies(request):
    """View and manage user's custom vocabulary words."""
    user = request.user
    user_words = UserVocabulary.objects.filter(user=user)
    
    return render(request, 'LangLens/my_vocabularies.html', {
        'user_words': user_words,
    })


@login_required(login_url='login')
def add_vocabulary(request):
    """Add a new vocabulary word."""
    user = request.user
    message = ''
    error = ''
    
    if request.method == 'POST':
        word = request.POST.get('word', '').strip()
        definition = request.POST.get('definition', '').strip()
        
        if not word:
            error = 'Word is required.'
        elif UserVocabulary.objects.filter(user=user, word__iexact=word).exists():
            error = f'You already have "{word}" in your vocabulary.'
        else:
            UserVocabulary.objects.create(
                user=user,
                word=word,
                definition=definition
            )
            message = f'"{word}" added to your vocabulary!'
            return redirect('my_vocabularies')
    
    return render(request, 'LangLens/add_vocabulary.html', {
        'message': message,
        'error': error,
    })


@login_required(login_url='login')
def edit_vocabulary(request, vocab_id):
    """Edit an existing vocabulary word."""
    user = request.user
    vocab = get_object_or_404(UserVocabulary, id=vocab_id, user=user)
    message = ''
    error = ''
    
    if request.method == 'POST':
        word = request.POST.get('word', '').strip()
        definition = request.POST.get('definition', '').strip()
        
        if not word:
            error = 'Word is required.'
        elif UserVocabulary.objects.filter(user=user, word__iexact=word).exclude(id=vocab_id).exists():
            error = f'You already have another word "{word}" in your vocabulary.'
        else:
            vocab.word = word
            vocab.definition = definition
            vocab.save()
            message = f'"{word}" updated successfully!'
            return redirect('my_vocabularies')
    
    return render(request, 'LangLens/edit_vocabulary.html', {
        'vocab': vocab,
        'message': message,
        'error': error,
    })


@login_required(login_url='login')
def delete_vocabulary(request, vocab_id):
    """Delete a vocabulary word."""
    user = request.user
    vocab = get_object_or_404(UserVocabulary, id=vocab_id, user=user)
    word_name = vocab.word
    
    if request.method == 'POST':
        vocab.delete()
        messages.success(request, f'"{word_name}" removed from your vocabulary.')
        return redirect('my_vocabularies')
    
    return render(request, 'LangLens/delete_vocabulary.html', {
        'vocab': vocab,
    })


@login_required
def user_logout(request):
    logout(request)
    return redirect('login')


# ----------------AI LOGIC------------

from django.http import JsonResponse
import requests
import json

def ai_chat_handler(request):

    if request.method == "POST":
        user_message = request.POST.get('content')
        
        # LM Studio URL
        url = "http://localhost:1234/v1/chat/completions"
        
        payload = {
            "model": "dolphin3.0-llama3.1-8b",
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a helpful assistant for the LangLens platform. Keep answers short."
                },
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7
        }

        try:
            response = requests.post(url, json=payload, timeout=30)
            data = response.json()
            ai_text = data['choices'][0]['message']['content']
            return JsonResponse({'ai_output': ai_text})
        except Exception as e:
            return JsonResponse({'ai_output': "Sorry, my local brain is offline right now."}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)



# ...existing code...
@login_required(login_url='login')
def generate_vocabulary_tts(request):
    """
    View to generate vocabulary list, details, TTS audio, and update Vocabulary model.
    
    Handles GET or POST requests. Returns JSON response with status.
    """
    messages = []
    
    # Generate vocabulary list with error handling
    try:
        vocabulary_list = generate_vocabulary_list()
        if isinstance(vocabulary_list, str) and vocabulary_list.startswith("Error"):
            raise ValueError(f"Failed to generate vocabulary list: {vocabulary_list}")
        messages.append(f"Generated vocabulary list: {vocabulary_list}")
    except Exception as e:
        return JsonResponse({'error': f"Error in generating vocabulary list: {str(e)}"}, status=500)
    
    # Get vocabulary details with error handling
    try:
        details = get_vocabulary_details(vocabulary_list)
        if not details:
            raise ValueError("No details retrieved for vocabulary list.")
        messages.append("Retrieved details for vocabulary.")
    except Exception as e:
        return JsonResponse({'error': f"Error in getting vocabulary details: {str(e)}"}, status=500)
    
    # Extract words from details and generate TTS
    words = [item.get('word') for item in details if isinstance(item, dict) and item.get('word')]
    if not words:
        return JsonResponse({'error': 'No valid words found in details.'}, status=400)
    
    audio_files = make_tts(words)
    messages.append(f"Generated {len(audio_files)} audio files.")
    
    # Add audio files to the Vocabulary model
    add_audio_to_vocabulary(details, audio_files, messages)
    
    return JsonResponse({'message': 'Vocabulary TTS generation completed.', 'details': messages})

def make_tts(word_list):
    """
    Generates TTS audio files for each word in the provided list.
    
    Args:
        word_list (list): A list of words (strings) to generate audio for.
    
    Returns:
        list: A list of filenames for the generated audio files.
    """
    audio_files = []
    language = 'en'
    slow_audio_speed = False
    
    # Ensure the output directory exists
    output_dir = "static/LangLens/audio/vocabulary_audio"
    os.makedirs(output_dir, exist_ok=True)
    
    for word in word_list:
        if not isinstance(word, str) or not word.strip():
            continue
        
        try:
            # Create TTS object
            tts_object = gTTS(text=word, lang=language, slow=slow_audio_speed)
            
            # Define filename
            filename = os.path.join(output_dir, f"{word}.mp3")
            
            # Save the audio file
            tts_object.save(filename)
            audio_files.append(filename)
        except Exception as e:
            pass  # Skip errors in view context
    
    return audio_files

def add_audio_to_vocabulary(details, audio_files, messages):
    for item in details:
        if isinstance(item, dict) and 'word' in item and 'category' in item and 'description' in item:
            word = item['word']
            category_name = item['category']
            description = item['description']
            audio_file = next((f for f in audio_files if os.path.basename(f).startswith(word)), None)
            if audio_file:
                try:
                    # Get or create category
                    category_obj, _ = Category.objects.get_or_create(name=category_name)
                    
                    # Get or create vocabulary entry
                    vocab_entry, created = Vocabulary.objects.get_or_create(word=word)
                    vocab_entry.category = category_obj
                    vocab_entry.definition = description
                    
                    # Save audio file
                    with open(audio_file, 'rb') as f:
                        vocab_entry.audio.save(os.path.basename(audio_file), File(f))
                    
                    vocab_entry.save()
                    messages.append(f"Updated Vocabulary entry for: {word}")
                except Exception as e:
                    messages.append(f"Error updating Vocabulary entry for '{word}': {str(e)}")

# ...existing code...