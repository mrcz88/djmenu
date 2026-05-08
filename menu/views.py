from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin
from .models import Item
from .forms import ItemForm

def item_detail(request, item_id):
    item = Item.objects.get(id=item_id)
    return render(request, 'menu/item_detail.html', {'item': item})

# Classe per dettaglio di un priodotto
# equivalente alla funzione item_detail

class ItemDetailView(DetailView):
    model = Item
    template_name = "menu/item_detail.html"
    context_object_name = "item"

    
@login_required
def create_item(request):
    if request.method == 'GET':
        item = ItemForm()
        return render(request, 'menu/create_item.html', {'form': item})
    elif request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.instance.creator = request.user
            form.save(commit=True)
            return redirect('menu:item_detail', item_id=form.instance.id)

class CreateItemView(CreateView):
    model = Item
    template_name = "menu/create_item.html"
    fields = ['item_name', 'item_desc', 'item_price', 'item_image']

    # Viene invocato dopo che il form è stato validato
    # e il metodo save() è stato chiamato.
    # Qui possiamo aggiungere logica extra, come impostare il creator dell'item.
    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)

    # Se non specificato, Django reindirizza alla pagina di successo
    # mediante il metodo get_absolute_url del modello.
    # success_url = reverse_lazy('menu:item_list')

@login_required
def update_item(request, item_id):
    form = ItemForm(request.POST or None, instance=Item.objects.get(id=item_id))
    if form.is_valid():
        form.save()
        return redirect('menu:update_item', item_id=item_id)
    return render(request, 'menu/update_item.html', {'form': form, 'item_id': item_id})

class UpdateItemView(UpdateView):
    model = Item
    # di default UpdateView usa il template update_form.html
    template_name = "menu/update_item.html"
    fields = ['item_name', 'item_desc', 'item_price', 'item_image']

# Create your views here.
def item_list(request):
    items = Item.objects.all()
    print(items)
    return render(request, 'menu/item_list.html', {'items': items})

# Classe per la lista dei prodotti
# equivalente alla funzione item_list
class ItemListView(ListView):
    model = Item
    template_name = 'menu/item_list.html'
    context_object_name = 'items'

@login_required
def delete_item(request, item_id):
    item = Item.objects.get(id=item_id)
    item.delete()
    return redirect('menu:item_list')


class DeleteItemView(DeleteView, UserPassesTestMixin):
    model = Item
    # di default DeleteView usa il template delete_form.html
    template_name = "menu/delete_item_with_confirm.html"
    success_url = reverse_lazy('menu:item_list')

    # Controlla se l'utente è il creator dell'item
    # Se non è il creator, non può cancellare l'item
    def test_func(self):
        return self.request.user == self.get_object().creator

    

@login_required
def delete_item_with_confirm(request, item_id):
    item = Item.objects.get(id=item_id)
    if request.method == "POST":
        item.delete()
        return redirect('menu:item_list')
    return render(request, "menu/delete_item_with_confirm.html", {'item' : item})