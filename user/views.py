from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import UserRegistrationSerializer, UserLoginSerializer
from .models import User

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
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            # 首先检查用户是否存在
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({'error': '该邮箱未注册'}, status=status.HTTP_401_UNAUTHORIZED)
            
            # 验证密码
            if not user.check_password(password):
                return Response({'error': '密码错误'}, status=status.HTTP_401_UNAUTHORIZED)
            
            # 验证用户是否激活
            if not user.is_active:
                return Response({'error': '账户未激活，请先激活账户'}, status=status.HTTP_401_UNAUTHORIZED)
            
            # 生成令牌
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': '登录成功',
                'user': {
                    'email': user.email,
                    'username': user.username
                },
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
