
# Create your tests here.
import os
from gtts import gTTS
from localllm import generate_vocabulary_list, get_vocabulary_details
from django.core.files import File
from .models import Vocabulary, Category

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
            print(f"Skipping invalid word: {word}")
            continue
        
        try:
            # Create TTS object
            tts_object = gTTS(text=word, lang=language, slow=slow_audio_speed)
            
            # Define filename
            filename = os.path.join(output_dir, f"{word}.mp3")
            
            # Save the audio file
            tts_object.save(filename)
            audio_files.append(filename)
            print(f"Generated audio for: {word}")
        except Exception as e:
            print(f"Error generating TTS for '{word}': {str(e)}")
    
    return audio_files

# Generate vocabulary list with error handling
try:
    vocabulary_list = generate_vocabulary_list()
    if isinstance(vocabulary_list, str) and vocabulary_list.startswith("Error"):
        raise ValueError(f"Failed to generate vocabulary list: {vocabulary_list}")
    print("Generated vocabulary list:", vocabulary_list)
except Exception as e:
    print(f"Error in generating vocabulary list: {str(e)}")
    exit(1)

# Get vocabulary details with error handling
try:
    details = get_vocabulary_details(vocabulary_list)
    if not details:
        raise ValueError("No details retrieved for vocabulary list.")
    print("Retrieved details for vocabulary.")
except Exception as e:
    print(f"Error in getting vocabulary details: {str(e)}")
    exit(1)



# Extract words from details and generate TTS
words = [item.get('word') for item in details if isinstance(item, dict) and item.get('word')]
if not words:
    print("No valid words found in details.")
    exit(1)

audio_files = make_tts(words)
print(f"Generated {len(audio_files)} audio files.")

# Add audio files to the Vocabulary model
def add_audio_to_vocabulary(details, audio_files):
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
                    print(f"Updated Vocabulary entry for: {word}")
                except Exception as e:
                    print(f"Error updating Vocabulary entry for '{word}': {str(e)}")






# Call the function to add audio to vocabulary
add_audio_to_vocabulary(details, audio_files)
