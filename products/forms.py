from django import forms
from .models import Product


class ProductAdminForm(forms.ModelForm):

    remove_image = forms.BooleanField(
        required=False,
        label="Remove Product Image"
    )

    class Meta:
        model = Product
        fields = [
            'name',
            'category',
            'description',
            'price',
            'stock',
            'image',
            'remove_image',
        ]

    def save(self, commit=True):

        product = super().save(commit=False)

        if self.cleaned_data.get('remove_image'):

            if product.image:

                product.image.delete(save=False)

            product.image = None

        if commit:
            product.save()

        return product