from django.shortcuts import redirect

class EnterpriseRequiredForAdminMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # Sempre permitir acessar login e logout
        if path.startswith('/admin/login/') or path.startswith('/admin/logout/'):
            return self.get_response(request)

        # ---------------------------------------------------------------------
        # 🔥 NOVO: se for superusuário, envia direto para /admin
        # ---------------------------------------------------------------------
        if request.user.is_authenticated and request.user.is_superuser:
            # Se já está no admin, libera
            if path.startswith('/admin/'):
                return self.get_response(request)

            # Se está em qualquer outro lugar, envia para o admin
            return redirect('/admin/')
        # ---------------------------------------------------------------------

        # Exige enterprise_id para acessar o admin (usuário comum)
        if path.startswith('/admin/'):
            enterprise_id = request.session.get('enterprise_id')

            if not enterprise_id:
                return redirect('/perfil/')

        return self.get_response(request)
