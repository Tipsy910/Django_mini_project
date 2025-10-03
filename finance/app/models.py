from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image

class Category(models.Model):
    CATEGORY_TYPE_CHOICES = [
        ('income', 'รายรับ'),
        ('expense', 'รายจ่าย'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=7, choices=CATEGORY_TYPE_CHOICES, default='expense')
    icon_name = models.CharField(max_length=50, blank=True, null=True)
    
    description = models.TextField(blank=True, null=True, help_text="คำอธิบายเพิ่มเติม (ถ้ามี)")
    color_code = models.CharField(max_length=7, blank=True, null=True, help_text="โค้ดสี เช่น #FF5733")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"


class Transaction(models.Model):
    """Model for income and expense transactions"""
    TRANSACTION_TYPES = [
        ('income', 'รายรับ'),
        ('expense', 'รายจ่าย'),
    ]
    
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('check', 'Check'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    transaction_date = models.DateTimeField(default=timezone.now)
    receipt_image = models.ImageField(upload_to='receipts/', blank=True, null=True)
    is_recurring = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-transaction_date']
    
    def __str__(self):
        return f"{self.title} - ${self.amount} ({self.transaction_type})"
    
    # --- เพิ่มคลาส Profile เข้าไปใหม่ ---
class Profile(models.Model):
    # เชื่อมกับ User แบบ One-to-One คือ 1 User มีได้ 1 Profile เท่านั้น
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # เพิ่ม fields ที่เราต้องการ
    bio = models.TextField(blank=True, null=True, help_text="เกี่ยวกับตัวฉัน")
    birth_date = models.DateField(null=True, blank=True, help_text="วันเกิด")
    # ImageField ต้องใช้ Pillow library (pip install Pillow)
    profile_picture = models.ImageField(default='default.jpg', upload_to='profile_pics')
    receive_newsletter = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.user.username} Profile'

    # 👈 --- 2. Override เมธอด save ---
    def save(self, *args, **kwargs):
        # บันทึกข้อมูลโปรไฟล์ตามปกติก่อน (เพื่อให้มีไฟล์รูปภาพจริงในระบบ)
        super().save(*args, **kwargs)

        # เปิดไฟล์รูปภาพที่เพิ่งบันทึกไป
        img = Image.open(self.profile_picture.path)

        # เช็คว่าขนาดของรูปภาพใหญ่กว่าที่เราต้องการหรือไม่
        if img.height > 300 or img.width > 300:
            output_size = (300, 300) # กำหนดขนาดสูงสุดที่ต้องการ (กว้าง, สูง)
            img.thumbnail(output_size) # ย่อขนาดโดยคงสัดส่วนเดิมไว้
            img.save(self.profile_picture.path)

# --- ส่วนนี้สำคัญมาก! ---
# สร้างฟังก์ชันให้สร้าง Profile อัตโนมัติทุกครั้งที่มี User ใหม่ถูกสร้าง
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# สร้างฟังก์ชันให้บันทึก Profile อัตโนมัติทุกครั้งที่ User ถูกบันทึก
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
