from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import User, Like, Match
from django.utils import timezone

User = get_user_model()

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

class UserSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'username', 'nickname', 'email', 'avatar', 'gender', 'birth_date', 'bio', 'age', 'avatar_url', 'location', 'interests')
        read_only_fields = ('id', 'username', 'email')
    
    def get_age(self, obj):
        if obj.birth_date:
            today = timezone.now().date()
            return today.year - obj.birth_date.year - ((today.month, today.day) < (obj.birth_date.month, obj.birth_date.day))
        return None
    
    def get_avatar_url(self, obj):
        if obj.avatar:
            return self.context['request'].build_absolute_uri(obj.avatar.url)
        return self.context['request'].build_absolute_uri('/static/images/default-avatar.png')

class AvatarUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('avatar',)
        
    def validate_avatar(self, value):
        # 验证文件大小（例如：限制为 2MB）
        if value.size > 2 * 1024 * 1024:
            raise serializers.ValidationError("文件大小不能超过 2MB")
        
        # 验证文件类型
        if not value.content_type in ['image/jpeg', 'image/png']:
            raise serializers.ValidationError("只支持 JPG 和 PNG 格式的图片")
        
        return value

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'gender', 'birth_date', 'bio')
        
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            gender=validated_data.get('gender', 'M'),
            birth_date=validated_data.get('birth_date'),
            bio=validated_data.get('bio', '')
        )
        return user

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ('id', 'from_user', 'to_user', 'created_at')
        read_only_fields = ('id', 'created_at')
    
    def validate(self, data):
        # 检查是否喜欢自己
        if data['from_user'] == data['to_user']:
            raise serializers.ValidationError("不能喜欢自己")
        
        # 检查是否已经喜欢过
        if Like.objects.filter(from_user=data['from_user'], to_user=data['to_user']).exists():
            raise serializers.ValidationError("已经喜欢过该用户")
        
        return data 

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ('id', 'user1', 'user2', 'status', 'created_at')
        read_only_fields = ('id', 'created_at') 