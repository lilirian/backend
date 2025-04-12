from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import User
import os
import tempfile
from PIL import Image

class AvatarUploadTests(TestCase):
    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 创建测试客户端
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # 创建测试图片
        self.image = Image.new('RGB', (100, 100))
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        self.image.save(self.temp_file)
        
    def test_avatar_upload_success(self):
        """测试成功上传头像"""
        url = reverse('user-upload-avatar')
        
        with open(self.temp_file.name, 'rb') as file:
            response = self.client.post(url, {'avatar': file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('avatar', response.data)
        self.assertTrue(os.path.exists(self.user.avatar.path))
        
    def test_avatar_upload_unauthorized(self):
        """测试未授权用户上传头像"""
        client = APIClient()
        url = reverse('user-upload-avatar')
        
        with open(self.temp_file.name, 'rb') as file:
            response = client.post(url, {'avatar': file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_avatar_upload_invalid_file(self):
        """测试上传无效文件"""
        url = reverse('user-upload-avatar')
        
        # 创建一个非图片文件
        invalid_file = SimpleUploadedFile("test.txt", b"file_content", content_type="text/plain")
        response = self.client.post(url, {'avatar': invalid_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_avatar_upload_no_file(self):
        """测试未上传文件"""
        url = reverse('user-upload-avatar')
        response = self.client.post(url, {}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def tearDown(self):
        # 清理测试文件
        if hasattr(self.user, 'avatar') and self.user.avatar:
            if os.path.exists(self.user.avatar.path):
                os.remove(self.user.avatar.path)
        self.temp_file.close()
