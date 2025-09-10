from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.home, name='home'),

    # 🔔 Notification
    path("notifications/", views.get_notifications, name="get_notifications"),
    path("notifications/mark-read/", views.mark_notifications_read, name="mark_notifications_read"),

    # 🩸 Posts & Comments
    path('pluse', views.pluse, name="pluse"),
    path("comments/<int:post_id>/", views.get_comments, name="get_comments"),
    path("comments/<int:post_id>/add/", views.add_comment, name="add_comment"),
    path("chat/users/", views.chat_users, name="chat_users"),
    path("chat/history/<int:user_id>/", views.chat_history, name="chat_history"),

    # 👑 Heroes
    path("heroes/", views.heroes, name="heroes"),
    path("heroes/<int:pk>/", views.hero_detail, name="hero_detail"),
path("chat/unread_count/", views.unread_count, name="unread_count"),
    # 📄 Static pages
    path("about/", views.about, name="about"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),

    # 👤 Auth & Profile
    path("register/", views.register, name="register"),  
    path('verify/<str:username>/', views.verify, name='verify'),
    path("login/", views.login_view, name="login"),

    # 🧑‍🤝‍🧑 Dashboards
    path('donor-dashboard/', views.donor_dashboard, name='donor_dashboard'),
    path('receiver-dashboard/', views.receiver_dashboard, name='receiver_dashboard'),
       path("chat/send/<int:user_id>/", views.send_message, name="send_message"),
    path("chat/poll/<int:user_id>/", views.poll_messages, name="poll_messages"),
    path("chat/history/<int:user_id>/", views.chat_history, name="chat_history"),
    path("chat/users/", views.chat_users, name="chat_users"),
    # 📩 Contact
    path("save-contact/", views.save_contact, name="save_contact"),

    # 🩸 Donation Flow
    path("donate/<int:post_id>/", views.donate_now, name="donate_now"),
    path("donation/<int:donation_id>/approve/", views.approve_donation, name="approve_donation"),
    path("donation/<int:donation_id>/reject/", views.reject_donation, name="reject_donation"),
    path("donation/<int:donation_id>/pending/", views.donation_pending, name="donation_pending"),
    path("manage-donations/", views.manage_donations, name="manage_donations"),
    path("approve-donation/<int:donation_id>/", views.approve_donation, name="approve_donation"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
