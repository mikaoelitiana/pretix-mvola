from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from mvola.core import Mvola as MvolaSDK
from mvola.tools import Transaction
from pretix.base.settings import SettingsSandbox

from pretix_mvola.models import MVolaOrderPayment


@csrf_exempt
@require_http_methods(["PUT"])
def callback(request, *args, **kwargs):
    reference = request.GET.get("reference")
    order_payment = MVolaOrderPayment.objects.get(reference=reference)
    if order_payment.payment:
        settings = SettingsSandbox("payment", "mvola", order_payment.order.event)
        api = MvolaSDK(
            settings.consumer_key,
            settings.secret_key,
            settings.status,
        )
        res = api.generate_token()
        if res.success:
            token = res.response
            transaction = Transaction(
                token=token,
                user_language="FR",
                user_account_identifier=order_payment.user_account_identifier,
                partner_name="pretix",
                server_correlation_id=order_payment.server_correlation_id,
            )
            res = api.status_transaction(transaction)
            if res.success:
                if res.response["status"] == "completed":
                    order_payment.payment.confirm()
                    return HttpResponse("Payment OK")
                else:
                    order_payment.payment.fail()
            else:
                print(f"Status_code [{res.status_code}] \n {res.error}")
        else:
            print(f"Status_code[{res.status_code}] \n {res.error}")
    return HttpResponse("Payment not found")
