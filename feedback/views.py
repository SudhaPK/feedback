from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import Feedback, Upvote

def index(request):
    """Main page - serves the SPA"""
    return render(request, 'feedback/index.html')

@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_feedbacks(request):
    """
    API endpoint for feedbacks
    GET: Return all feedbacks with vote info
    POST: Create new feedback
    """
    if request.method == 'GET':
        # Get current user from query params
        current_user = request.GET.get('username', '')
        
        # Get all feedbacks with upvote info
        feedbacks_data = []
        for feedback in Feedback.objects.all():
            feedbacks_data.append({
                'id': feedback.id,
                'content': feedback.content,
                'username': feedback.username,
                'created_at': feedback.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'upvote_count': feedback.get_upvote_count(),
                'user_has_voted': feedback.user_has_voted(current_user)
            })
        
        return JsonResponse({'feedbacks': feedbacks_data})
    
    elif request.method == 'POST':
        # Create new feedback
        try:
            data = json.loads(request.body)
            content = data.get('content', '').strip()
            username = data.get('username', '').strip()
            
            # Simple validation
            if not content or not username:
                return JsonResponse({'error': 'Content and username required'}, status=400)
            
            if len(content) < 5:
                return JsonResponse({'error': 'Feedback too short (min 5 chars)'}, status=400)
            
            # Create feedback
            feedback = Feedback.objects.create(
                content=content,
                username=username
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Feedback created successfully',
                'feedback': {
                    'id': feedback.id,
                    'content': feedback.content,
                    'username': feedback.username,
                    'created_at': feedback.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'upvote_count': 0,
                    'user_has_voted': False
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_toggle_vote(request, feedback_id):
    """
    Toggle upvote for a feedback
    If user hasn't voted: add vote
    If user has voted: remove vote
    """
    try:
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        
        if not username:
            return JsonResponse({'error': 'Username required'}, status=400)
        
        # Get feedback
        try:
            feedback = Feedback.objects.get(id=feedback_id)
        except Feedback.DoesNotExist:
            return JsonResponse({'error': 'Feedback not found'}, status=404)
        
        # Check if user already voted
        upvote_exists = Upvote.objects.filter(
            feedback=feedback, 
            username=username
        ).first()
        
        if upvote_exists:
            # Remove vote
            upvote_exists.delete()
            action = 'removed'
            user_has_voted = False
        else:
            # Add vote
            Upvote.objects.create(
                feedback=feedback,
                username=username
            )
            action = 'added'
            user_has_voted = True
        
        return JsonResponse({
            'success': True,
            'action': action,
            'upvote_count': feedback.get_upvote_count(),
            'user_has_voted': user_has_voted
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
