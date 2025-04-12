from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView, UserLoginView, MatchViewSet, 
    UserViewSet, UserProfileView, get_likes_list
)

urlpatterns = [
    path('match/likes/', get_likes_list, name='get_likes_list'),
]

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'match', MatchViewSet, basename='match')

urlpatterns += [
    path('', include(router.urls)),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='profile'),
] 