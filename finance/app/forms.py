# app/forms.py

from django import forms
from .models import Transaction, Category,Profile
from django.contrib.auth.models import User

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        # เลือก field ที่จะให้ผู้ใช้กรอกข้อมูล
        fields = [
            'transaction_type', 
            'title', 
            'amount', 
            'category', 
            'transaction_date', 
            'description'
        ]
        labels = {
            'transaction_type': 'ประเภทรายการ',
            'title': 'หัวข้อ',
            'amount': 'จำนวนเงิน',
            'category': 'หมวดหมู่',
            'transaction_date': 'วันที่ทำรายการ',
            'description': 'คำอธิบาย',
        }
        
        widgets = {
            # ใช้วิดเจ็ต HTML5 date input เพื่อให้มีปฏิทินให้เลือก
            'transaction_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border rounded-md'}),
        }

    def __init__(self, *args, **kwargs):
        # รับ user ที่ login อยู่เข้ามาจาก view
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # กรอง Category ให้แสดงเฉพาะของผู้ใช้คนนั้นๆ
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)
        
        # เพิ่ม class ของ Tailwind ให้กับ field อื่นๆ
        for field_name in self.fields:
            if field_name != 'transaction_date': # ไม่ต้องทำซ้ำกับ date ที่กำหนดใน widget แล้ว
                self.fields[field_name].widget.attrs.update({
                    'class': 'w-full px-3 py-2 border rounded-md'
                })

ICON_CHOICES = [
    ('', '--- เลือกไอคอน ---'),
    ('fa-solid fa-utensils', 'อาหาร'),
    ('fa-solid fa-car', 'การเดินทาง'),
    ('fa-solid fa-house', 'ที่อยู่อาศัย'),
    ('fa-solid fa-film', 'ความบันเทิง'),
    ('fa-solid fa-cart-shopping', 'ช้อปปิ้ง'),
    ('fa-solid fa-wallet', 'เงินเดือน'),
    ('fa-solid fa-gift', 'ของขวัญ/โบนัส'),
    ('fa-solid fa-ellipsis', 'อื่นๆ'),
]

class CategoryForm(forms.ModelForm):
    # ---- จุดที่แก้ไข ----
    # ทำให้ icon_name เป็น ChoiceField ธรรมดา โดยไม่กำหนด widget
    # มันจะกลายเป็น <select> (Dropdown) โดยอัตโนมัติ
    icon_name = forms.ChoiceField(
        choices=ICON_CHOICES, 
        required=False, 
        label="เลือกไอคอน"
    )
    # --------------------

    class Meta:
        model = Category
        fields = ['name', 'category_type', 'icon_name', 'color_code', 'description']
        
        labels = {
            'name': 'ชื่อประเภท',
            'category_type': 'ชนิดของประเภท',
            'color_code': 'เลือกสี',
            'description': 'คำอธิบาย',
        }
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'category_type': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'color_code': forms.TextInput(attrs={'type': 'color', 'class': 'w-full h-10 p-1 border border-gray-300 rounded-md cursor-pointer'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        # เพิ่ม class ให้กับ icon_name ที่ตอนนี้เป็น Dropdown แล้ว
        self.fields['icon_name'].widget.attrs.update(
            {'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}
        )

FORM_CONTROL_CLASS = "mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': FORM_CONTROL_CLASS}),
            'email': forms.EmailInput(attrs={'class': FORM_CONTROL_CLASS}),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        # 'profile_picture' จะถูกจัดการใน template โดยตรง
        fields = ['bio', 'birth_date', 'profile_picture', 'receive_newsletter']
        widgets = {
            'bio': forms.Textarea(attrs={'class': FORM_CONTROL_CLASS, 'rows': 4}),
            'birth_date': forms.DateInput(attrs={'class': FORM_CONTROL_CLASS, 'type': 'date'}),
        }