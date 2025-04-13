from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserSerializer, LikeSerializer, AvatarUploadSerializer, MatchSerializer
from .models import User, Like, Match
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.http import FileResponse
from django.conf import settings
import os
from django.utils import timezone
import requests
import json

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
            
            # 首先检查用户是否存在（支持邮箱登录）
            try:
                user = User.objects.get(Q(username=username) | Q(email=username))
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
            # 重新获取用户信息，确保返回最新的头像URL
            user_serializer = UserSerializer(request.user, context={'request': request})
            return Response({
                'status': 'success',
                'message': '头像上传成功',
                'data': user_serializer.data
            })
        return Response({
            'status': 'error',
            'message': '上传失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

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
            'from_user': request.user,
            'to_user': to_user
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

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            user = request.user
            serializer = UserSerializer(user, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        try:
            user = request.user
            serializer = UserSerializer(user, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def optimize(self, request):
        try:
            user = request.user
            # 获取用户的基本信息
            basic_info = {
                'nickname': user.username,
                'age': self.calculate_age(user.birth_date),
                'gender': user.gender,
                'bio': user.bio,
                'interests': user.interests.split(',') if user.interests else []
            }
            
            # 分析用户资料
            suggestions = self.analyze_profile(basic_info)
            
            # 生成优化建议
            optimized_bio = self.generate_optimized_bio(basic_info)
            
            return Response({
                'suggestions': suggestions,
                'optimized_bio': optimized_bio,
                'keywords': self.extract_keywords(optimized_bio)
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def calculate_age(self, birth_date):
        if not birth_date:
            return None
        today = timezone.now().date()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    
    def analyze_profile(self, basic_info):
        suggestions = []
        
        # 检查昵称
        if not basic_info['nickname'] or len(basic_info['nickname']) < 2:
            suggestions.append('建议设置一个更有特色的昵称')
        
        # 检查年龄
        if not basic_info['age']:
            suggestions.append('建议完善年龄信息')
        
        # 检查个人介绍
        if not basic_info['bio']:
            suggestions.append('建议添加个人介绍')
        elif len(basic_info['bio']) < 50:
            suggestions.append('建议丰富个人介绍内容')
        
        # 检查兴趣爱好
        if not basic_info['interests']:
            suggestions.append('建议添加兴趣爱好')
        elif len(basic_info['interests']) < 3:
            suggestions.append('建议添加更多兴趣爱好')
        
        return suggestions
    
    def generate_optimized_bio(self, basic_info):
        # 根据用户信息生成优化后的个人介绍
        bio_parts = []
        
        # 添加基本信息
        if basic_info['nickname']:
            bio_parts.append(f"我是{basic_info['nickname']}")
        
        if basic_info['age']:
            bio_parts.append(f"今年{basic_info['age']}岁")
        
        # 添加兴趣爱好
        if basic_info['interests']:
            interests_str = '、'.join(basic_info['interests'])
            bio_parts.append(f"喜欢{interests_str}")
        
        # 添加个人介绍
        if basic_info['bio']:
            bio_parts.append(basic_info['bio'])
        
        # 添加结尾
        bio_parts.append("希望能在这里遇到志同道合的朋友")
        
        return '，'.join(bio_parts)
    
    def extract_keywords(self, text):
        # 简单的关键词提取
        keywords = []
        common_words = {'的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
        
        words = text.split('，')
        for word in words:
            if len(word) > 1 and word not in common_words:
                keywords.append(word)
        
        return keywords[:5]  # 返回前5个关键词

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_likes_list(request):
    """
    获取当前用户的喜欢列表
    """
    try:
        # 获取当前用户的所有喜欢记录
        likes = Like.objects.filter(from_user=request.user)
        
        # 获取被喜欢用户的信息
        liked_users = []
        for like in likes:
            user = like.to_user
            liked_users.append({
                'id': user.id,
                'username': user.username,
                'nickname': user.nickname,
                'avatar_url': request.build_absolute_uri(user.avatar.url) if user.avatar else None,
                'age': user.age,
                'location': user.location,
                'interests': user.interests
            })
            
        return Response({
            'code': 200,
            'message': '获取成功',
            'data': liked_users
        })
    except Exception as e:
        return Response({
            'code': 500,
            'message': str(e)
        }, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def optimize_profile(request):
    """
    使用腾讯元宝API优化用户个人简介
    """
    try:
        # 获取当前用户
        user = request.user
        user_profile = UserProfile.objects.get(user=user)
        
        # 获取当前简介
        current_bio = user_profile.bio or ""
        
        # 调用腾讯元宝API
        url = 'https://open.hunyuan.tencent.com/openapi/v1/agent/chat/completions'
        headers = {
            'X-Source': 'openapi',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer eDJrUI9XpQ64LjgMweTfoYh5DqIXJcAc'
        }
        
        data = {
            "assistant_id": "nDPb8gDN9hXy",
            "user_id": str(user.id),
            "stream": False,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"请帮我优化以下个人简介，使其更加吸引人，同时保持原有的核心信息：{current_bio}"
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=data)
        response_data = response.json()
        
        if response.status_code == 200:
            optimized_bio = response_data['choices'][0]['message']['content']
            
            # 更新用户简介
            user_profile.bio = optimized_bio
            user_profile.save()
            
            return Response({
                'status': 'success',
                'message': '个人简介优化成功',
                'optimized_bio': optimized_bio
            })
        else:
            return Response({
                'status': 'error',
                'message': 'API调用失败',
                'error': response_data
            }, status=response.status_code)
            
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    try:
        user = request.user
        serializer = UserSerializer(user, context={'request': request})
        return Response({
            'status': 'success',
            'data': serializer.data
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    try:
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True, context={'request': request})
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': '个人资料更新成功',
                'data': serializer.data
            })
        return Response({
            'status': 'error',
            'message': '数据验证失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
