from django.template.loader import (
    render_to_string
)

from django.urls import reverse

from django.utils.http import (
    urlsafe_base64_encode
)

from django.utils.encoding import (
    force_bytes
)

from django.contrib.auth.tokens import (
    default_token_generator
)

def send_activation_email(request, user):
    uid = urlsafe_base64_encode(
        force_bytes(user.pk)
    )
    token = default_token_generator.make_token(
        user
    )
    activation_link = request.build_absolute_uri(
        reverse(
            'activate-account',
            kwargs={
                'uidb64': uid,
                'token': token
            }
        )
    )

    html_content = render_to_string(
        'signup/activation_email.html',
        {
            'user': user,
            'activation_link': activation_link
        }

    )

    print('\n')
    print('================ EMAIL =================')
    print(html_content)
    print('========================================')
    print('\n')