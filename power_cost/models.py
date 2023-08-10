from django.db import models


class Rate(models.Model):
    group = models.ForeignKey("auth.group", on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=50)
    rate = models.DecimalField(decimal_places=2, max_digits=8)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class RatePeriod(models.Model):
    # Pairing of Rates to Time
    rate = models.ForeignKey("Rate", on_delete=models.CASCADE, null=False)
    start_hour = models.IntegerField()
    end_hour = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
