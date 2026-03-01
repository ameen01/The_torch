from django.shortcuts import render, get_object_or_404
from .models import Vocabulary, Category, ListingModule, ReadingModule
from django.http import JsonResponse
import requests
import json

# Create your views here.
def index(request):
    return render(request, 'LangLens/index.html')



def home(request):
    return render(request, 'LangLens/index.html')


def sign_in(request):
    return render(request, 'LangLens/login.html')


def resgitor(request):
    return render (request, 'LangLens/signup.html')


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
    
    # Get the template from the dictionary, default to news if not found
    template_path = templates.get(text.category.name, 'LangLens/reading_news.html')
    return render(request,template_path, {'text': text})

def get_vocbulary_categories(request):
    excluded_category = ['News', 'Emails', 'Short stories']
    categories = Category.objects.exclude(name__in=excluded_category)
    return render(request, 'LangLens/vocabulary_category.html', {'categories':categories})


def display_vocabulary_list(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    vocabularies = Vocabulary.objects.filter(category=category)
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
    
    # Get the template from the dictionary, default to news if not found
    template_path = templates.get(text.category.name, 'LangLens/listening_stories.html')
    return render(request,template_path, {'text': text})


def writing(request, ):
    return render(request, 'LangLens/writing.html')

def dashboard(request):
    return render(request, 'LangLens/dashboard.html')


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