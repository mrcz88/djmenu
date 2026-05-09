from django.urls import path

from . import views

app_name = "menu"

urlpatterns = [
    #path('', views.ItemListView.as_view(), name='index'),

    path('', views.item_list_paginated, name='index'),
    path('items/', views.item_list_paginated, name='item_list'),
    #path('items/', views.ItemListView.as_view(), name='item_list'),
    # equivalente:
    # path('items/', views.item_list, name='item_list'),

    # Dettaglio di un prodotto. NOta che il parametro pk è il primary key del prodotto.
    path('items/<int:pk>/', views.ItemDetailView.as_view(), name='item_detail'),
    # equivalente:
    #path('items/<int:item_id>/', views.item_detail, name='item_detail'),
    
    #path('items/update/<int:item_id>/', views.update_item, name='update_item'),
    path('items/update/<int:pk>/', views.UpdateItemView.as_view(), name='update_item'),
    
    #path('items/create/', views.CreateItemView.as_view(), name='create_item'),
    path('items/create/', views.create_item, name='create_item'),

    #path('items/delete/<int:item_id>/', views.delete_item, name='delete_item'),
    #path('items/safedelete/<int:item_id>/', views.delete_item_with_confirm, name='delete_item_with_confirm'),
    path('items/safedelete/<int:pk>/', views.DeleteItemView.as_view(), name='delete_item_with_confirm'),

    path('items/favorite/<int:pk>/', views.favorite_item, name='favorite_item'),

]
