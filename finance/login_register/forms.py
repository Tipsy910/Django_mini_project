# login_register/forms.py

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

input_css_class = "w-full px-3 py-2 placeholder-gray-400 border border-gray-300 rounded-md shadow-sm appearance-none focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"

class RegistrationForm(forms.ModelForm):
    # สร้าง field password และ password2 เพิ่มเติม
    password = forms.CharField(
        label="รหัสผ่าน", 
        widget=forms.PasswordInput(attrs={'class': input_css_class})
    )
    password2 = forms.CharField(
        label="ยืนยันรหัสผ่าน", 
        widget=forms.PasswordInput(attrs={'class': input_css_class})
    )

    class Meta:
        model = User
        fields = ('username', 'email') # field ที่จะบันทึกลง model โดยตรง
        widgets = {
            'username': forms.TextInput(attrs={'class': input_css_class, 'placeholder': 'ชื่อผู้ใช้ของคุณ'}),
            'email': forms.EmailInput(attrs={'class': input_css_class, 'placeholder': 'your@email.com'}),
        }
        labels = {
            'username': 'ชื่อผู้ใช้',
            'email': 'อีเมล',
        }

    def clean_username(self):
        """ตรวจสอบว่า username นี้มีคนใช้แล้วหรือยัง"""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("ชื่อผู้ใช้นี้มีคนใช้งานแล้ว")
        return username

    def clean_password2(self):
        """ตรวจสอบว่ารหัสผ่าน 2 ช่องตรงกันหรือไม่"""
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password2 and password != password2:
            raise ValidationError("รหัสผ่านไม่ตรงกัน")
        return password2

    def save(self, commit=True):
        """เข้ารหัสรหัสผ่านก่อนบันทึก"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user