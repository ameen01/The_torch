from .models import UserProfile

def profile_context(request):
    """Add user profile to all template contexts"""
    profile = None
    if request.user.is_authenticated:
        profile = UserProfile.objects.filter(user=request.user).first()
    return {'profile': profile}