from collections import OrderedDict
from django import forms
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from pretix.base.forms import SecretKeySettingsField
from pretix.base.signals import register_global_settings, register_payment_providers


@receiver(register_payment_providers, dispatch_uid="payment_mvola")
def register_payment_provider(sender, **kwargs):
    from .payment import MVola

    return MVola


@receiver(register_global_settings, dispatch_uid="payment_mvola_global_settings")
def register_global_settings(sender, **kwargs):
    return OrderedDict(
        [
            (
                "payment_mvola_consumer_key",
                forms.CharField(
                    label=_("Mvola: Consumer key"),
                    required=True,
                ),
            ),
            (
                "payment_mvola_secret_key",
                SecretKeySettingsField(
                    label=_("Mvola: Secret Key"),
                    required=True,
                ),
            ),
            (
                "payment_mvola_status",
                forms.ChoiceField(
                    label=_("Mvola: Status"),
                    initial="live",
                    choices=(
                        ("SANDBOX", "SANDBOX"),
                        ("PRODUCTION", "PRODUCTION"),
                    ),
                ),
            ),
            (
                "payment_mvola_receiver_number",
                forms.CharField(label=_("Mvola: Receiver phone number"), required=True),
            ),
        ]
    )
