from django.shortcuts import render, redirect
# --- เปลี่ยนชื่อฟอร์มตรงนี้ ---
from .forms import RegistrationForm 
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

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