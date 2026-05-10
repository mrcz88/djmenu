from django.contrib.auth.models import User
from django.db.models import Avg, Count, Max, Sum
from django.http import JsonResponse
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

from rest_framework import viewsets
from rest_framework.views import APIView, status

from menu.serializers import ItemSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import permissions
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Item
from .forms import ItemForm
from .permissions import IsCreatorOrReadOnly

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

# NON DRF
def item_list_json(request):
    items = Item.objects.all().values('id', 'item_name', 'item_price')
    return JsonResponse(list(items), safe=False)

# LIST AND CREATE API = = = =  = = = = = = = = = = = = = 

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    # Altre permissions sono: IsAuthenticated, AllowAny, IsAdminUser, DjangoModelPermissions, DjangoModelPermissionsOrAnonReadOnly
    # IsAuthenticatedOrReadOnly permette di leggere i dati senza autenticarsi
    # IsAuthenticated permette di leggere e scrivere i dati solo se si è autenticati
    # AllowAny permette di leggere e scrivere i dati senza autenticarsi
    # IsAdminUser permette di leggere e scrivere i dati solo se si è admin
    # DjangoModelPermissions permette di leggere e scrivere i dati solo se si ha i permessi di Django
    # DjangoModelPermissionsOrAnonReadOnly permette di leggere i dati senza autenticarsi e scrivere i dati solo se si ha i permessi di Django
    permission_classes = [IsCreatorOrReadOnly]
    # Di default prende tutte le authentication classes definite in settings.py
    authentication_classes = [TokenAuthentication, JWTAuthentication]


    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

class ItemListCreateAPIView(generics.ListCreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)
class ItemListAPIView(APIView):
    def post(self, request):
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(creator=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def get(self, request):
        items = Item.objects.all()
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)

@api_view(['GET', 'POST'])
def item_list_api(request):
    if request.method == 'GET':
        items = Item.objects.all()
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        # Nota la mancanza di many=True perché stiamo creando un singolo item
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(creator=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# DETAIL AND UPDATE AND DELETE API = = = = = = = = = = = = = = = = = = = = = = = = = 


class ItemRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

class ItemDetailAPIView(APIView):
    def get(self, request, pk):
        item = Item.objects.get(id=pk)
        serializer = ItemSerializer(item)
        return Response(serializer.data)
    def put(self, request, pk):
        item = Item.objects.get(id=pk)
        serializer = ItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.instance.creator = request.user
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, pk):
        item = Item.objects.get(id=pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'PUT', 'DELETE'])
def item_detail_api(request, pk):
    if request.method == 'GET':
        item = Item.objects.get(id=pk)
        serializer = ItemSerializer(item)
        return Response(serializer.data)
    elif request.method == 'PUT':
        item = Item.objects.get(id=pk)
        serializer = ItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.instance.creator = request.user
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        item = Item.objects.get(id=pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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