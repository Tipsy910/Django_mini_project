from django.shortcuts import render, redirect
# --- เปลี่ยนชื่อฟอร์มตรงนี้ ---
from .forms import RegistrationForm ,PasswordResetRequestForm, SetNewPasswordForm
from django.contrib.auth import login, authenticate, logout,update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm,PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings


def register_view(request):
    if request.method == 'POST':
        # --- และตรงนี้ ---
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "สมัครสมาชิกสำเร็จ!")
            return redirect('app:dashboard')
        else:
            # ไม่ต้องแสดง error message ตรงนี้ เพราะฟอร์มจะจัดการเอง
            pass
    else:
        # --- และตรงนี้ ---
        form = RegistrationForm()
    return render(request, 'login_register/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"ยินดีต้อนรับคุณ {username} เข้าสู่ระบบ")
                return redirect('app:dashboard') 
            else:
                messages.error(request, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
        else:
            messages.error(request, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
    form = AuthenticationForm()
    return render(request, 'login_register/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "คุณได้ออกจากระบบแล้ว")
    return redirect('login_register:login')

@login_required
def password_change_view(request):
    if request.method == 'POST':
        # ถ้ามีการส่งฟอร์มมา ให้ประมวลผล
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            # ถ้ารหัสผ่านถูกต้องตามเงื่อนไข
            user = form.save() # บันทึกรหัสผ่านใหม่
            
            # *** สำคัญมาก ***
            # อัปเดต session ของผู้ใช้ เพื่อไม่ให้หลุดออกจากระบบ
            update_session_auth_hash(request, user)  
            
            messages.success(request, 'รหัสผ่านของคุณถูกเปลี่ยนเรียบร้อยแล้ว!')
            return redirect('app:dashboard') # หรือไปหน้าโปรไฟล์
        else:
            # ถ้าฟอร์มไม่ถูกต้อง (เช่น รหัสเก่าผิด, รหัสใหม่ไม่ตรงกัน)
            messages.error(request, 'กรุณาแก้ไขข้อผิดพลาดด้านล่าง')
    else:
        # ถ้าเป็นการเข้าหน้าเว็บครั้งแรก ให้แสดงฟอร์มเปล่า
        form = PasswordChangeForm(request.user)
        
    return render(request, 'login_register/password_change.html', {
        'form': form
    })
    
def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)

                # สร้าง Token และ UID
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # สร้างลิงก์สำหรับรีเซ็ต
                reset_link = request.build_absolute_uri(f'/password-reset-confirm/{uid}/{token}/')
                
                # เตรียมเนื้อหาอีเมลจาก Template
                email_subject = 'คำขอตั้งรหัสผ่านใหม่'
                email_body = render_to_string('password_reset/email_body.html', {
                    'user': user,
                    'reset_link': reset_link,
                })
                
                # ส่งอีเมล
                send_mail(
                    email_subject,
                    email_body,
                    settings.DEFAULT_FROM_EMAIL, # <-- 2. เปลี่ยนมาใช้ค่าจาก settings.py
                    [user.email]
                )
                
                messages.success(request, 'เราได้ส่งลิงก์สำหรับตั้งรหัสผ่านใหม่ไปที่อีเมลของคุณแล้ว')
                return redirect('login_register:login') # หรือหน้า "ตรวจสอบอีเมล"

            except User.DoesNotExist:
                # ไม่ต้องแจ้งว่าไม่มีอีเมลนี้ในระบบ เพื่อความปลอดภัย
                messages.success(request, 'หากอีเมลนี้มีอยู่ในระบบ เราได้ส่งลิงก์ไปให้แล้ว')
                return redirect('login_register:login')
    else:
        form = PasswordResetRequestForm()
        
    return render(request, 'password_reset/request_form.html', {'form': form})


# 2. View สำหรับยืนยันและตั้งรหัสผ่านใหม่
def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetNewPasswordForm(request.POST)
            if form.is_valid():
                user.set_password(form.cleaned_data['new_password1'])
                user.save()
                messages.success(request, 'เปลี่ยนรหัสผ่านสำเร็จ! กรุณาเข้าสู่ระบบด้วยรหัสผ่านใหม่')
                return redirect('login_register:password_reset_done') 
        else:
            # จัดตำแหน่ง else นี้ให้อยู่ระดับเดียวกับ if request.method == 'POST'
            form = SetNewPasswordForm()

        # จัดตำแหน่ง return นี้ให้อยู่ระดับเดียวกับ if request.method == 'POST'
        return render(request, 'password_reset/confirm_form.html', {'form': form, 'validlink': True})
    else:
        messages.error(request, 'ลิงก์สำหรับตั้งรหัสผ่านใหม่ไม่ถูกต้องหรือหมดอายุแล้ว')
        # เพิ่ม context validlink=False เพื่อให้ template แสดงผลได้ถูกต้องเสมอ (เผื่อไว้)
        return render(request, 'password_reset/confirm_form.html', {'validlink': False})

def password_reset_done(request):
    
    return render(request, 'password_reset/request_done.html')
   