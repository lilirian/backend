from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    GENDER_CHOICES = (
        ('M', '男'),
        ('F', '女'),
    )
    
    # 基本信息
    nickname = models.CharField(max_length=50, default='用户', verbose_name='昵称')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M', verbose_name='性别')
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', verbose_name='头像')
    birth_date = models.DateField(null=True, blank=True, verbose_name='出生日期')
    location = models.CharField(max_length=100, null=True, blank=True, verbose_name='所在地')
    
    # 个人简介
    bio = models.TextField(max_length=500, null=True, blank=True, verbose_name='个人简介')
    interests = models.CharField(max_length=200, null=True, blank=True, verbose_name='兴趣爱好')
    
    # 匹配相关
    last_active = models.DateTimeField(default=timezone.now, verbose_name='最后活跃时间')
    is_online = models.BooleanField(default=False, verbose_name='是否在线')
    
    email = models.EmailField(_('email address'), unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.nickname

class Like(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes_sent', verbose_name='喜欢者')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes_received', verbose_name='被喜欢者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '喜欢关系'
        verbose_name_plural = verbose_name
        unique_together = ('from_user', 'to_user')  # 防止重复喜欢
        
    def __str__(self):
        return f"{self.from_user} 喜欢 {self.to_user}"

class Match(models.Model):
    STATUS_CHOICES = (
        ('pending', '待确认'),
        ('accepted', '已接受'),
        ('rejected', '已拒绝'),
    )
    
    user1 = models.ForeignKey(User, related_name='matches_initiated', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='matches_received', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user1', 'user2')
    
    def __str__(self):
        return f"Match between {self.user1} and {self.user2}"
