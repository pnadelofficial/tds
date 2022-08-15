from django.urls import path
from . import views

urlpatterns = [
    path("", views.forum_index, name="forum_index"),
    path("<int:pk>/", views.forum_detail, name="forum_detail"),
    path("<category>/", views.forum_category, name="forum_category"),
    #path("notebook/", views.notebook_test, name="notebook_test")
]