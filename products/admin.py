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

    # ======================================================
    # 🔥 EXIBIR DOMÍNIO APÓS O NOME (apenas superusuário)
    # ======================================================
    def get_enterprise_domain(self, obj):
        return obj.enterprise.domain if obj.enterprise else "-"
    get_enterprise_domain.short_description = "Domínio"
    get_enterprise_domain.admin_order_field = "enterprise__domain"

    def get_list_display(self, request):
        base = list(self.list_display)

        if not request.user.is_superuser:
            return tuple(base)

        # inserir após o campo name
        if "name" in base:
            idx = base.index("name") + 1
            base.insert(idx, "get_enterprise_domain")
        else:
            base.insert(0, "get_enterprise_domain")

        return tuple(base)

    # ======================================================
    # FILTRA PRODUTOS PELA ENTERPRISE DO USUÁRIO COMUM
    # ======================================================
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        enterprise_id = request.session.get("enterprise_id")
        return qs.filter(enterprise_id=enterprise_id)

    # ======================================================
    # REMOVE O CAMPO ENTERPRISE PARA NÃO SUPERUSUÁRIO
    # ======================================================
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)

        if not request.user.is_superuser:
            return [f for f in fields if f != "enterprise"]

        return fields

    # ======================================================
    # GARANTE QUE O ENTERPRISE VEM DA SESSÃO AO SALVAR
    # ======================================================
    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.enterprise_id = request.session.get("enterprise_id")
        super().save_model(request, obj, form, change)

    # ======================================================
    # FORMATAÇÕES
    # ======================================================
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
