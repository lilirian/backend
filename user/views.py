from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserSerializer, LikeSerializer, AvatarUploadSerializer, MatchSerializer
from .models import User, Like, Match
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.http import FileResponse
from django.conf import settings
import os

User = get_user_model()

# Create your views here.

class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': '注册成功',
                'user': {
                    'email': user.email,
                    'username': user.username
                },
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            # 首先检查用户是否存在
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({'error': '用户不存在'}, status=status.HTTP_401_UNAUTHORIZED)
            
            # 验证密码
            if not user.check_password(password):
                return Response({'error': '密码错误'}, status=status.HTTP_401_UNAUTHORIZED)
            
            # 生成令牌
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user, context={'request': request}).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['post'])
    def upload_avatar(self, request):
        serializer = AvatarUploadSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserSerializer(request.user, context={'request': request}).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def avatar(self, request, pk=None):
        user = self.get_object()
        if not user.avatar:
            return Response({'error': '用户没有头像'}, status=status.HTTP_404_NOT_FOUND)
        
        avatar_path = user.avatar.path
        if not os.path.exists(avatar_path):
            return Response({'error': '头像文件不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        return FileResponse(open(avatar_path, 'rb'), content_type='image/jpeg')

    @action(detail=False, methods=['get'])
    def matches(self, request):
        matches = Match.objects.filter(user1=request.user) | Match.objects.filter(user2=request.user)
        serializer = MatchSerializer(matches, many=True)
        return Response(serializer.data)

class MatchViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        """
        获取推荐用户列表
        1. 排除自己
        2. 排除已经喜欢过的用户
        3. 只推荐异性
        4. 按最后活跃时间排序
        """
        current_user = request.user
        liked_users = Like.objects.filter(from_user=current_user).values_list('to_user', flat=True)
        
        # 获取异性用户
        opposite_gender = 'F' if current_user.gender == 'M' else 'M'
        recommended_users = User.objects.filter(
            gender=opposite_gender
        ).exclude(
            id=current_user.id
        ).exclude(
            id__in=liked_users
        ).order_by('-last_active')
        
        serializer = UserSerializer(recommended_users, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def like(self, request):
        """
        喜欢某个用户
        """
        to_user_id = request.data.get('to_user_id')
        if not to_user_id:
            return Response({'error': '需要指定用户ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            to_user = User.objects.get(id=to_user_id)
        except User.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # 创建喜欢关系
        like_data = {
            'from_user': request.user.id,
            'to_user': to_user.id
        }
        
        serializer = LikeSerializer(data=like_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def matches(self, request):
        """
        获取互相喜欢的用户列表（匹配成功）
        """
        # 获取我喜欢的用户
        liked_by_me = Like.objects.filter(from_user=request.user).values_list('to_user', flat=True)
        # 获取喜欢我的用户
        liked_me = Like.objects.filter(to_user=request.user).values_list('from_user', flat=True)
        # 获取互相喜欢的用户ID
        matched_user_ids = set(liked_by_me) & set(liked_me)
        
        # 获取用户信息
        matched_users = User.objects.filter(id__in=matched_user_ids)
        serializer = UserSerializer(matched_users, many=True, context={'request': request})
        return Response(serializer.data)
