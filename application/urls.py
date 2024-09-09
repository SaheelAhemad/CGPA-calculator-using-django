from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('get_data/', views.get_data, name='get_data'),
    path('display_results/', views.display_results, name='display_results'),
    path('select_semester/', views.select_semester, name='select_semester'),
    path('edit_semester/', views.get_data, name='edit_semester'),  # Use get_data for editing
    path('view_results/', views.display_results, name='view_results'),
]
