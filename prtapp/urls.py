from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("signup/student/", views.student_signup, name="student_signup"),
    path("signup/investor/", views.investor_signup, name="investor_signup"),
    path("post-idea/", views.post_idea, name="post_idea"),
    path("dashboard/", views.dashboard, name="dashboard"),

      # Is path ko prtapp/urls.py ke urlpatterns list ke andar add karein
    path('express-interest/<int:idea_id>/', views.express_interest, name='express_interest'),
    # Is path ko prtapp/urls.py ke urlpatterns ke andar jodna hai
    path('find-team/', views.find_team_register, name='find_team_register'),

    # Add these two paths to your prtapp/urls.py list

    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

  

] 


