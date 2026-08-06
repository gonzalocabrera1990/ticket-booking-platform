from django.urls import path
from .views import login_view, account_not_verified_view, resend_activation_email_view, verify_login_code_view, logout_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path(
        '',
        login_view,
        name='login'
    ),
    path(
        'account-not-verified/',
        account_not_verified_view,
        name='account-not-verified'
    ),
    path(
        'resend-activation-email/',
        resend_activation_email_view,
        name='resend-activation-email'
    ),
    path(
        'verify-login/',
        verify_login_code_view,
        name='verify-login'
    ),
    path(
        'logout/',
        logout_view,
        name='logout'
    ),
    # 1. Pantalla donde el usuario ingresa su email
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(template_name='login/password_reset_form.html'), 
         name='password_reset'),
    
    # 2. Pantalla que dice "Te enviamos un mail con las instrucciones"
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='login/password_reset_done.html'), 
         name='password_reset_done'),
    
    # 3. El link secreto que le llega al mail (valida el Token criptográfico en la URL)
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='login/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    
    # 4. Pantalla de éxito: "Tu contraseña fue cambiada, ya podés iniciar sesión"
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='login/password_reset_complete.html'), 
         name='password_reset_complete'),
]
