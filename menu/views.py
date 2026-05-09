from django.db.models import Avg, Count, Max, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.cache import cache_page
import logging
from .models import Item
from .forms import ItemForm

logger = logging.getLogger(__name__)

def item_detail(request, item_id):
    logger.info("item_detail")
    logger.info(request.GET)
    logger.info("Fetching item from database")
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
            return redirect('menu:item_detail', pk=form.instance.id)
        else:
            logger.error(form.errors)
            return render(request, 'menu/create_item.html', {'form': form})

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
    # utilizziamo select_related per ottimizzare le query 
    # e prefetch_related per ottimizzare le query dei tag 
    # (In pratica eseguira un query per ottenere gli item e un query per ottenere i tag)
    #
    items = Item.objects.all()\
        .select_related('creator')\
        .prefetch_related('tags')\
        .annotate(num_favorites=Count('favorited_by'))\
        .order_by('-item_created_at')
    return render(request, 'menu/item_list.html', {'items': items})


@cache_page(60) # cache di 1 minuto
def item_list_paginated(request):
    # Item è un QuerySet, quindi possiamo usarlo con Paginator
    # Un QuerySet è un oggetto che contiene i risultati di una query ma non esegue la query
    # L'applicazione del Paginator equivale a fare un LIMIT nella query SQL
    # e un OFFSET nella query SQL
    logger.info("item_list_paginated")
    logger.info(request.GET)
    logger.info("Fetching items from database")
    items = Item.objects.all()\
        .select_related('creator')\
        .prefetch_related('tags')\
        .annotate(num_favorites=Count('favorited_by'))\
        .order_by('-item_created_at')
    logger.debug(f"Found {items.count()} items")
    paginator = Paginator(items, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'menu/item_list_paginated.html', {'page_obj': page_obj})

# Classe per la lista dei prodotti
# equivalente alla funzione item_list
class ItemListView(ListView):
    model = Item
    template_name = 'menu/item_list.html'
    context_object_name = 'items'

@login_required
def delete_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    item.delete()
    return redirect('menu:item_list')


class DeleteItemView(UserPassesTestMixin, DeleteView):
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
    try: 
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        logger.error(f"Item with id {item_id} does not exist")
        return redirect('menu:item_list')
    if request.method == "POST":
        item.delete()
        return redirect('menu:item_list')
    return render(request, "menu/delete_item_with_confirm.html", {'item' : item})

@login_required
def favorite_item(request, pk):
    pass

def cheaper_than_kebab(request):
    items = Item.objects.filter(item_price__lt=10).order_by('-item_price')
    return render(request, 'menu/cheaper_than_kebab.html', {'items': items})

def user_has_created_item(request):
    is_creator = Item.objects.filter(creator=request.user).order_by('-item_created_at').exists()
    return render(request, 'menu/user_has_created_item.html', {'is_creator': is_creator})
    
def spicy_items(request):
    items = Item.objects\
        .filter(item_desc__icontains='piccante')\
        .values("id", "item_name", "item_price")\
        .order_by('-item_price')
    return render(request, 'menu/spicy_items.html', {'items': items})

def item_in_range(request, min_price, max_price):
    items = Item.objects.filter(item_price__range=(min_price, max_price)).order_by('-item_price')
    return render(request, 'menu/item_in_range.html', {'items': items})

def item_by_first_letter(request, letter):
    items = Item.objects.filter(item_name__startswith=letter).order_by('-item_price')
    return render(request, 'menu/item_by_first_letter.html', {'items': items})

def items_created_in_the_last_week(request):
    start = (timezone.now() - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
    items = Item.objects.filter(item_created_at__gte=start).order_by('-item_price')
    return render(request, 'menu/items_created_in_the_last_week.html', {'items': items})

def average_price(request):
    average = Item.objects.aggregate(Avg('item_price'))['item_price__avg']
    return render(request, 'menu/average_price.html', {'average': average})

def total_price(request):
    total = Item.objects.aggregate(Sum('item_price'))['item_price__sum']
    return render(request, 'menu/total_price.html', {'total': total})

def max_price(request):
    max = Item.objects.aggregate(Max('item_price'))['item_price__max']
    return render(request, 'menu/max_price.html', {'max': max})