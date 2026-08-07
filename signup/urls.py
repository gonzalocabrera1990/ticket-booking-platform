from django.urls import path
from .views import (
    signup_view,
    address_signup_view,
    email_verification_sent,
    #activate,
    load_regions,
    load_cities,
    activate_account_view,
)

urlpatterns = [
    path(
        '',
        signup_view,
        name='signup'
    ),
    path(
        'address/',
        address_signup_view,
        name='address-signup'
    ),
    path(
        'activate/<uidb64>/<token>/',
        activate_account_view,
        name='activate-account'
    ),
    path(
        'email-sent/',
        email_verification_sent,
        name='email-verification-sent'
    ),
    path(
        'ajax/load-regions/',
        load_regions,
        name='ajax-load-regions'
    ),
    path(
        'ajax/load-cities/',
        load_cities,
        name='ajax-load-cities'
    ),
]