# eventsharer_admin/context_processors.py
from .models import Event




def user_events(request):
    """
    Adds the current user's events to the template context, including
    invite URL, photo count, and contributor count.
    """
    if request.user.is_authenticated:
        events = Event.objects.filter(user=request.user).order_by('-date')
        events_with_url = [
            {
                'event': event,
                'invite_url': event.get_invite_url(request),
                'photo_count': event.photo_count,
                'contributor_count': event.contributor_count,
            }
            for event in events
        ]
    else:
        events_with_url = []

    return {'user_events': events_with_url}


