from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from organization.models import Enterprise

@login_required
def perfil(request):
    # Buscar todas empresas onde o usuário é membro
    enterprises = Enterprise.objects.filter(
        members__user=request.user
    ).distinct()

    context = {
        "enterprises": enterprises,
    }

    return render(request, "perfil/perfil.html", context)



@login_required
def selecionar_empresa(request, enterprise_id):
    """
    Salva a empresa que o usuário clicou na sessão 
    e redireciona para o admin.
    """
    request.session["enterprise_id"] = str(enterprise_id)
    request.session.modified = True

    return redirect("/admin/")
