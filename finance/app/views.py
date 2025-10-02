# app/views.py

from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import Transaction, Category
from .forms import TransactionForm , CategoryForm# เพิ่ม form ที่เราสร้าง
from django.shortcuts import get_object_or_404 
from django.db.models.functions import TruncMonth # เพิ่ม import นี้
from collections import defaultdict # เพิ่ม import นี้
from django.db.models import Sum # เพิ่ม import นี้
from .forms import UserUpdateForm, ProfileUpdateForm # เราจะสร้างฟอร์มนี้ในขั้นตอนถัดไป
from django.contrib import messages


@login_required
def dashboard_view(request):
    transactions = Transaction.objects.filter(user=request.user)
    
    # ... โค้ดคำนวณยอดรวมและเตรียมข้อมูล Pie chart เดิม ...
    expense_transactions = transactions.filter(transaction_type='expense')
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expense = sum(t.amount for t in expense_transactions)
    net_balance = total_income - total_expense
    expense_by_category = expense_transactions.values('category__name').annotate(total=Sum('amount'))
    chart_labels = [item['category__name'] for item in expense_by_category]
    chart_data = [float(item['total']) for item in expense_by_category]

    # --- เตรียมข้อมูลสำหรับกราฟเส้น (Line Chart) ---
    # 1. จัดกลุ่มและรวมยอดธุรกรรมตามเดือนและประเภท (รายรับ/รายจ่าย)
    monthly_data = transactions.annotate(month=TruncMonth('transaction_date')) \
        .values('month', 'transaction_type') \
        .annotate(total_amount=Sum('amount')) \
        .order_by('month')

    # 2. ประมวลผลข้อมูลเพื่อหายอดสุทธิของแต่ละเดือน
    monthly_summary = defaultdict(lambda: {'income': 0, 'expense': 0})
    for item in monthly_data:
        month = item['month'].strftime('%b %Y') # จัดรูปแบบเดือน เช่น "Sep 2025"
        monthly_summary[month][item['transaction_type']] = float(item['total_amount'])

    line_chart_labels = list(monthly_summary.keys())
    line_chart_data = [v['income'] - v['expense'] for v in monthly_summary.values()]
    
    context = {
        'transactions': transactions,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_balance': net_balance,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        # --- ส่งข้อมูลกราฟเส้นไปที่ Template ---
        'line_chart_labels': line_chart_labels,
        'line_chart_data': line_chart_data,
    }
    
    return render(request, 'app/dashboard.html', context)

@login_required
def add_transaction_view(request):
    if request.method == 'POST':
        # ส่ง user เข้าไปในฟอร์มเพื่อกรอง category
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            # ยังไม่บันทึกลง DB จริงๆ เพราะต้องใส่ user ก่อน
            transaction = form.save(commit=False)
            # กำหนดให้ transaction นี้เป็นของ user ที่ login อยู่
            transaction.user = request.user
            # บันทึกลง DB
            transaction.save()
            return redirect('app:dashboard') # กลับไปหน้า dashboard
    else:
        # ส่ง user เข้าไปในฟอร์มเพื่อกรอง category
        form = TransactionForm(user=request.user)
        
    return render(request, 'app/add_transaction.html', {'form': form})

@login_required
def add_category_view(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            # ยังไม่บันทึกลง DB เพื่อกำหนดค่า user ก่อน
            category = form.save(commit=False)
            # กำหนดให้ category นี้เป็นของ user ที่ login อยู่
            category.user = request.user
            category.save()
            # กลับไปหน้าเพิ่ม Transaction (เพื่อให้เลือก category ใหม่ได้เลย)
            return redirect('app:category_list')
    else:
        form = CategoryForm()
        
    return render(request, 'app/add_category.html', {'form': form})

@login_required
def category_list_view(request):
    """แสดง Category ทั้งหมดของผู้ใช้"""
    categories = Category.objects.filter(user=request.user).order_by('name')
    return render(request, 'app/category_list.html', {'categories': categories})

@login_required
def edit_category_view(request, pk):
    """แก้ไข Category ที่มีอยู่"""
    # ดึงข้อมูลโดยเช็คว่าเป็นของ user คนนี้จริงหรือไม่ เพื่อความปลอดภัย
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('app:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'app/add_category.html', {'form': form, 'is_edit': True})

@login_required
def delete_category_view(request, pk):
    """ลบ Category (รับเฉพาะ POST request)"""
    category = get_object_or_404(Category, pk=pk, user=request.user)
    category.delete()
    # ไม่ต้องมี if request.method == 'POST' อีกต่อไป
    return redirect('app:category_list')

@login_required
def edit_transaction_view(request, pk):
    """แก้ไข Transaction ที่มีอยู่"""
    # ดึงข้อมูล transaction โดยเช็คว่าเป็นของ user คนนี้จริงหรือไม่
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    
    if request.method == 'POST':
        # ส่ง user และ instance เข้าไปในฟอร์ม
        form = TransactionForm(request.POST, instance=transaction, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        # ส่ง user และ instance เข้าไปในฟอร์มเพื่อแสดงข้อมูลเดิม
        form = TransactionForm(instance=transaction, user=request.user)
        
    # เราจะใช้ template `add_transaction.html` ซ้ำ แต่ส่ง context เพิ่ม
    return render(request, 'app/add_transaction.html', {'form': form, 'is_edit': True})

@login_required
def delete_transaction_view(request, pk):
    """ลบ Transaction"""
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        transaction.delete()
        return redirect('app:dashboard')
    return render(request, 'app/transaction_confirm_delete.html', {'transaction': transaction})

@login_required # <-- decorator นี้จะทำให้หน้านี้เข้าได้เฉพาะคนที่ login แล้วเท่านั้น
def profile_view(request):
    # ไม่ต้องทำอะไรซับซ้อน เพราะเราเรียกใช้ user.profile ได้จาก template โดยตรง
    # เราแค่ render template ออกไปก็พอ
    return render(request, 'app/profile.html')

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        # รับข้อมูลจากฟอร์มที่ส่งมา
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, 
                                   request.FILES, # สำหรับรับไฟล์รูปภาพ
                                   instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'โปรไฟล์ของคุณถูกอัปเดตเรียบร้อยแล้ว!')
            return redirect('app:profile') # กลับไปที่หน้า profile หลังบันทึกสำเร็จ
    else:
        # แสดงฟอร์มพร้อมข้อมูลปัจจุบัน
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'app/edit_profile.html', context)