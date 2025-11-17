from django.contrib import admin
from .models import Product
from .forms import ProductForm


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    
    form = ProductForm

    list_display = ("name", "get_price_display", "stock", "is_active", "get_created_short")
    list_display_links = ("name",)
    search_fields = ("name", "description")
    list_filter = ("is_active", "created_at")
    readonly_fields = ("slug",)
    ordering = ("-created_at",)
    exclude = ("enterprise",)

    class Media:
        js = ("js/price_mask.js",)

    @staticmethod
    def get_price_display(obj):
        if obj.price is None:
            return "R$ 0,00"
        formatted = f"R$ {obj.price:,.2f}"
        return formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    get_price_display.short_description = "Preço"
    get_price_display.admin_order_field = "price"

    @staticmethod
    def get_created_short(obj):
        if not obj.created_at:
            return "-"
        return obj.created_at.strftime("%d/%m/%y %H:%M")
    get_created_short.short_description = "Criado em"
    get_created_short.admin_order_field = "created_at"
