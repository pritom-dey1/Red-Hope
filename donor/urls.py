from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [

    path('', views.home, name='home'),
    path('pluse', views.pluse, name = "pluse"),
        path("comments/<int:post_id>/", views.get_comments, name="get_comments"),
    path("comments/<int:post_id>/add/", views.add_comment, name="add_comment"),
    path("heroes/",views.heroes ,name = "heroes"),
    path("heroes/<int:pk>/", views.hero_detail, name="hero_detail"),
    path("about/",views.about ,name = "about"),
     path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("register/", views.register, name="register"),  
     path('verify/<str:username>/', views.verify, name='verify'),
    path('donor-dashboard/', views.donor_dashboard, name='donor_dashboard'),
    path('receiver-dashboard/', views.receiver_dashboard, name='receiver_dashboard'),
       path("login/", views.login_view, name="login"),
     path("save-contact/", views.save_contact, name="save_contact"),              
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
