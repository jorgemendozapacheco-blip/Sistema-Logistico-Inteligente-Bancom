from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, get_user_model
from .forms import LoginForm
from django.contrib import messages

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            username = cd['username']
            password = cd['password']

            User = get_user_model()
            user_exists = User.objects.filter(username=username).exists()

            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('academico:dashboard')
                else:
                    messages.warning(request, "Tu cuenta está inactiva. Contacta al administrador.")
            else:
                # Si el usuario existe pero la contraseña es incorrecta:
                if user_exists:
                    messages.error(request, "Tu contraseña no es correcta. Vuelve a comprobarla.")
                else:
                    # Usuario no existe
                    messages.error(request, "Usuario o contraseña incorrectos.")
        else:
            messages.error(request, "Por favor, completa todos los campos.")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})