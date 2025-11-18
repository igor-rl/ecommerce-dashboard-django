from django.contrib import admin
from .models import Product
from .forms import ProductForm
from organization.models import Enterprise


class ProductAdmin(admin.ModelAdmin):

    form = ProductForm

    list_display = ("name", "get_price_display", "stock", "is_active", "get_created_short")
    list_display_links = ("name",)
    search_fields = ("name", "description")
    list_filter = ("is_active", "created_at")
    readonly_fields = ("slug",)
    ordering = ("-created_at",)

    class Media:
        js = ("js/price_mask.js",)

    # ----------------------------------------------------------
    # FILTRA PRODUTOS POR enterprise_id (igual agendas/atendimentos)
    # ----------------------------------------------------------
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs

        enterprise_id = request.session.get("enterprise_id")
        return qs.filter(enterprise_id=enterprise_id)

    # ----------------------------------------------------------
    # REMOVE O CAMPO ENTERPRISE DO FORMULÁRIO (usuário comum)
    # ----------------------------------------------------------
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if not request.user.is_superuser:
            return [f for f in fields if f != "enterprise"]
        return fields

    # ----------------------------------------------------------
    # GARANTE QUE O ENTERPRISE VEM DA SESSÃO AO SALVAR
    # ----------------------------------------------------------
    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.enterprise_id = request.session.get("enterprise_id")
        super().save_model(request, obj, form, change)

    # ----------------------------------------------------------
    # FORMATAÇÕES
    # ----------------------------------------------------------
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


admin.site.register(Product, ProductAdmin)
