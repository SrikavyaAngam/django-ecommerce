from django.db import models


class Product(models.Model):

    CATEGORY_CHOICES = [
        ("mobile", "Mobile"),
        ("laptop", "Laptop"),
        ("tablet", "Tablet"),
        ("headphones", "Headphones"),
        ("smartwatch", "Smartwatch"),
        ("camera", "Camera"),
        ("television", "Television"),
        ("speaker", "Speaker"),
        ("computer_accessories", "Computer Accessories"),
        ("gaming", "Gaming"),
    ]

    name = models.CharField(max_length=255)

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES
    )

    description = models.TextField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    stock = models.PositiveIntegerField(default=0)

    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name