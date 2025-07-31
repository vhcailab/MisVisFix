from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('set-image-session/', views.set_image_session, name='set_image_session'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('api/key-issues/', views.get_key_issues, name='get_key_issues'),
    path('api/fetch-gpt-image/', views.fetch_gpt_image, name='fetch_gpt_image'),
    path('api/chat-api/', views.chat_api, name='api/chat-api/'),
    path('api/upload-dataset/', views.upload_dataset, name='api/upload-dataset/'),
    path('api/get-dataset/', views.fetch_get_dataset, name='api/get-dataset/'),
    path('api/fetch-claude-image/', views.fetch_claude_image, name='fetch_claude_image'),
    path('api/set-learning-messgae/', views.set_thread_instructions, name='set-learning-messgae'),
    path("check-run-status/", views.check_run_status, name="check-run-status"),
    path("api/learn-text/", views.save_learn_content, name="learn-text"),
    path('api/learn-all-messages/', views.save_messages, name='learn-all-messages'),
    path('api/add-new-issue/', views.add_new_issue, name='add-new-issue'),
    path('gallery', views.gallery_page, name='gallery'),
    path('api/images/', views.gallery_api, name='gallery_api'),
    path('view/<int:index>/', views.view_image, name='view_image'),
    path('api/analyze-chart/', views.analyze_chart_code, name='analyze_chart_code'),
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    path('save-user-api-keys-session', views.save_user_api_keys_session, name='save_user_api_keys_session'),
    path('how_to_setup_key/', views.how_it_setup_key, name='how_to_setup_key'),
]
