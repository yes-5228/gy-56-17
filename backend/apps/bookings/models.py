from django.db import models

from apps.routes.models import TravelRoute


class Booking(models.Model):
    STATUS_CHOICES = [
        ("pending", "待确认"),
        ("confirmed", "已确认"),
        ("cancelled", "已取消"),
    ]

    route = models.ForeignKey(TravelRoute, related_name="bookings", on_delete=models.CASCADE)
    contact_name = models.CharField("联系人", max_length=60)
    phone = models.CharField("手机号", max_length=30)
    party_size = models.PositiveIntegerField("报名人数", default=1)
    travel_date = models.DateField("出行日期")
    status = models.CharField("状态", max_length=20, choices=STATUS_CHOICES, default="pending")
    remark = models.CharField("备注", max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "id"]

    def __str__(self):
        return f"{self.contact_name} - {self.route.title}"


class Traveler(models.Model):
    ID_TYPE_CHOICES = [
        ("id_card", "身份证"),
        ("passport", "护照"),
        ("hk_macau", "港澳通行证"),
        ("taiwan", "台湾通行证"),
        ("other", "其他"),
    ]

    booking = models.ForeignKey(Booking, related_name="travelers", on_delete=models.CASCADE)
    name = models.CharField("姓名", max_length=60)
    id_type = models.CharField("证件类型", max_length=20, choices=ID_TYPE_CHOICES, default="id_card")
    id_number = models.CharField("证件号码", max_length=50)
    age = models.PositiveIntegerField("年龄", null=True, blank=True)
    special_requirements = models.CharField("特殊需求", max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.name} ({self.get_id_type_display()})"
