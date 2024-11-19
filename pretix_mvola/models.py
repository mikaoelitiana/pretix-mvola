from django.db import models


class MVolaOrderPayment(models.Model):
    server_corelation_id = models.CharField(max_length=190, db_index=True, unique=True)
    reference = models.CharField(max_length=20, db_index=True, unique=True)
    order = models.ForeignKey("pretixbase.Order", on_delete=models.CASCADE)
    payment = models.ForeignKey(
        "pretixbase.OrderPayment", null=True, blank=True, on_delete=models.CASCADE
    )
