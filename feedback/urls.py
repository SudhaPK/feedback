from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/feedbacks/', views.api_feedbacks, name='api_feedbacks'),
    path('api/feedbacks/<int:feedback_id>/vote/', views.api_toggle_vote, name='api_toggle_vote'),
]