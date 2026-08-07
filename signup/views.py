from django.http import JsonResponse

from .models import User
from cities_light.models import Country
from cities_light.models import Region
from cities_light.models import City

from django.shortcuts import (
    render,
    redirect
)
from .utils import (
    send_activation_email
)

from django.contrib.auth import login

from .forms import (
    SignUpForm,
    AddressForm
)
# imports para verificar email

from django.utils.http import (
    urlsafe_base64_decode
)

from .tokens import (
    account_activation_token
)

from django.utils.encoding import (
    force_str
)
from django.contrib.auth.tokens import (
    default_token_generator
)
from .decorators import (
    unauthenticated_user
)
from django.contrib import messages

@unauthenticated_user
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(
            request.POST,
            request.FILES
        )
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            request.session[
                'pending_user_id'
            ] = user.id
            return redirect('address-signup')

    else:
        form = SignUpForm()

    return render(
        request,
        'signup/signup.html',
        {
            'form': form
        }
    )

@unauthenticated_user
def address_signup_view(request):
    user_id = request.session.get(
        'pending_user_id'
    )
    if not user_id:
        return redirect('signup')

    user = User.objects.get(
        id=user_id
    )

    countries = Country.objects.all()

    if request.method == 'POST':
        form = AddressForm(
            request.POST
        )
        if form.is_valid():
            address = form.save(
                commit=False
            )
            address.user = user
            if not user.addresses.exists():
                address.is_default = True

            address.save()
            send_activation_email(
                request,
                user
            )

            return redirect(
                'email-verification-sent'
            )

    else:
        form = AddressForm()

    return render(
        request,
        'signup/address.html',
        {
            'form': form,
            'countries': countries,
        }
    )

@unauthenticated_user
def email_verification_sent(request):
    return render(
        request,
        'signup/email_sent.html'
    )

@unauthenticated_user
def activate_account_view(request, uidb64, token):
    try:
        uid = force_str(
            urlsafe_base64_decode(
                uidb64
            )
        )
        user = User.objects.get(
            pk=uid
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
        User.DoesNotExist
    ):
        user = None

    if (user is not None and default_token_generator.check_token(user,token)):
        user.is_active = True
        user.save()
        # MENSAJE DE ÉXITO EN EL LOGIN
        messages.success(request, '¡Tu cuenta ha sido activada con éxito! Ya podés ingresar tus credenciales.')
        return redirect(
            'login'
        )

    else:
        return render(
            request,
            'signup/activation_invalid.html'
        )

def load_regions(request):
    country_id = request.GET.get('country')
    regions = Region.objects.filter(
        country_id=country_id
    ).values(
        'id',
        'name'
    )
    return JsonResponse(
        list(regions),
        safe=False
    )

def load_cities(request):
    region_id = request.GET.get('region')
    cities = City.objects.filter(
        region_id=region_id
    ).values(
        'id',
        'name'
    ).order_by('name')

    return JsonResponse(
        list(cities),
        safe=False
    )
