from datetime import datetime

from pprint import pprint
from collections import OrderedDict
from django import forms
from django.http import HttpRequest
from django.utils.translation import gettext as _
from django.utils.crypto import get_random_string
from mvola.core import Mvola as MvolaSDK
from mvola.tools import Transaction
from pretix.base.models import Event
from pretix.base.payment import BasePaymentProvider, OrderPayment
from pretix.base.settings import SettingsSandbox
from pretix.multidomain.urlreverse import build_absolute_uri

from pretix_mvola.models import MVolaOrderPayment


class MVola(BasePaymentProvider):
    identifier = "mvola"
    verbose_name = _("MVola")
    payment_form_fields = OrderedDict([])
    execute_payment_needs_user = True
    test_mode_message = _(
        """No real money will be used for testing.
         You can check https://www.mvola.mg/devportal
         for more details on test payments."""
    )

    def __init__(self, event: Event):
        super().__init__(event)
        self.settings = SettingsSandbox("payment", "mvola", event)
        self.api = MvolaSDK(
            self.settings.consumer_key,
            self.settings.secret_key,
            self.settings.status,
        )

    def get_access_token(self, request):
        res = self.api.generate_token()
        if res.success:
            request.session["mvola_token"] = res.response
        else:
            print(f"Status_code[{res.status_code}] \n {res.error}")

    def checkout_prepare(self, request, cart):
        # This payment method only supports MGA currency
        if self.event.currency != "MGA":
            print(f"{self.event.currency} currency is not supported by MVola")
            return False
        self.get_access_token(request)
        form = self.payment_form(request)
        if form.is_valid() and request.session["mvola_token"]:
            request.session["reference"] = f"{request.event.id}-{get_random_string(12)}"
            request.session["mvola_cart_total"] = int(cart["total"])
            request.session["mvola_callbackurl"] = build_absolute_uri(
                request.event, "plugins:pretix_mvola:callback", kwargs={}
            )
            request.session["mvola_debit_account_number"] = form.cleaned_data[
                "debit_account_number"
            ]
            return True
        return False

    def checkout_confirm_render(self, request):
        return _("You will need to validate the payment on your mobile phone.")

    def payment_is_valid_session(self, request):
        return True

    def execute_payment(self, request: HttpRequest, payment: OrderPayment):
        now = datetime.now()
        self.transaction = Transaction(
            token=request.session["mvola_token"],
            user_language="FR",
            user_account_identifier=request.session["mvola_debit_account_number"],
            partner_name="pretix",
            amount=request.session["mvola_cart_total"],
            x_callback_url=request.session["mvola_callbackurl"],
            currency="Ar",
            description_text=f"ORDER_{payment.order.code}",
            debit=request.session["mvola_debit_account_number"],
            credit=self.settings.receiver_number,
            request_date=now.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            original_transaction_reference=payment.order.code,
            requesting_organisation_transaction_reference=payment.order.code,
        )

        res = self.api.init_transaction(self.transaction)

        if res.success:
            # This will be used to find the payment on notify
            reference = MVolaOrderPayment(
                payment=payment,
                server_correlation_id=res.response["serverCorrelationId"],
                reference=request.session["reference"],
                order=payment.order,
            )
            reference.save()

        else:
            print(f"Status_code [{res.status_code}] \n {res.error}")

    @property
    def payment_form_fields(self):
        return OrderedDict(
            [
                (
                    "debit_account_number",
                    forms.CharField(
                        label=_("Your MVola account number"),
                        required=True,
                    ),
                ),
            ]
        )
