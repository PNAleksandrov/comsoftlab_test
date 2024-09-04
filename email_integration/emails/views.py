from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .forms import EmailAccountForm
from .models import EmailAccount


def email_list(request):
    if request.method == 'POST':
        form = EmailAccountForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user, created = User.objects.get_or_create(username=email, defaults={'email': email})

            # Проверяем, существует ли уже аккаунт с таким email
            existing_account = EmailAccount.objects.filter(email=email).first()
            if existing_account:
                # Если аккаунт существует, обновляем пароль
                existing_account.password = password
                existing_account.save()
            else:
                # Если аккаунта нет, создаем новый
                EmailAccount.objects.create(user=user, email=email, password=password)

            return redirect('email_consumer', account_id=EmailAccount.objects.get(email=email).id)
    else:
        form = EmailAccountForm()

    return render(request, 'email_form.html', {'form': form})


def email_consumer(request, account_id):
    return render(request, 'email_list.html', {'account_id': account_id})