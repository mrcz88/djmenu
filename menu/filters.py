import django_filters
from django_filters import FilterSet
from django.db.models import Q

from .models import Item


class ItemFilter(FilterSet):
    min_price = django_filters.NumberFilter(field_name="item_price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="item_price", lookup_expr="lte")
    min_created_at = django_filters.DateFilter(field_name="item_created_at", lookup_expr="gte")
    max_created_at = django_filters.DateFilter(field_name="item_created_at", lookup_expr="lte")

    # Campi su cui filtrare
    class Meta:
        model = Item
        fields = []
