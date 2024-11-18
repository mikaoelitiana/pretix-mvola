import requests
import time
from collections import OrderedDict
from django.http import HttpRequest
from django.utils.crypto import get_random_string
from django.utils.translation import gettext as _
from pretix.base.models import Event
from pretix.base.payment import BasePaymentProvider, OrderPayment
from pretix.base.settings import SettingsSandbox
from pretix.multidomain.urlreverse import build_absolute_uri

from mvola.core import Mvola as MvolaSDK
from mvola.tools import Transaction
from requests.models import to_key_val_list

# from pretix_orange_money_mdg.models import ReferencedOrangeMoneyObject


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
        if request.session["mvola_token"]:
            request.session["mvola_cart_total"] = cart["total"]
            request.session["mvola_callbackurl"] = build_absolute_uri(
                request.event, "plugins:pretix_mvola:callback_url", kwargs={}
            )
            return True
        return False

    def checkout_confirm_render(self, request):
        return _("You will need to validate the payment on your mobile phone.")

    def payment_is_valid_session(self, request):
        return True

    def execute_payment(self, request: HttpRequest, payment: OrderPayment):
        self.transaction = Transaction(
            token=request.session["mvola_token"],
            user_language="FR",
            user_account_identifier="0343500003",  # [UserAccountIdentifier] Requiered fields
            partner_name="pretix",
            amount=request.session["mvola_cart_total"],
            x_callback_url=request.session["mvola_callbackurl"],
            currency="Ar",
            description_text=request,
            debit="0343500003",
            credit=self.settings.receiver_number,
        )

        # This will be used to find the payment on notify
        res = self.api.init_transaction(self.transaction)

        if res.success:
            print(res.response)
        else:
            print(f"Status_code [{res.status_code}] \n {res.error}")

    # reference = ReferencedOrangeMoneyObject(
    #     payment=payment,
    #     reference=request.session["orange_money_mdg_notif_token"],
    #     order=payment.order,
    # )
    # reference.save()
    # return request.session.get("orange_money_mdg_payment_url") or ""
