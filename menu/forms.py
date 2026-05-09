from django import forms
from .models import Item

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['item_name', 'item_price', 'item_desc', 'item_image']
        labels = {
            'item_name': 'Nome',
            'item_price': 'Prezzo',
            'item_desc': 'Descrizione',
            'item_image': 'Immagine'
        }
        widgets = {
            'item_name': forms.TextInput(attrs={
                'class': 'w-full rounded border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm placeholder:text-slate-400 focus:border-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900/20',
                'placeholder': 'Nome del prodotto'
            }),
            'item_price': forms.NumberInput(attrs={
                'class': 'w-full rounded border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm placeholder:text-slate-400 focus:border-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900/20',
                'placeholder': 'Prezzo del prodotto'
            }),
            'item_desc': forms.Textarea(attrs={
                'rows': 4,
                'class': 'w-full rounded border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm placeholder:text-slate-400 focus:border-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900/20',
                'placeholder': 'Descrizione del prodotto'
            }),
            'item_image': forms.URLInput(attrs={
                'class': 'w-full rounded border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm placeholder:text-slate-400 focus:border-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900/20',
                'placeholder': 'URL dell\'immagine del prodotto'
            }),
        }
    def clean_item_price(self):
        item_price = self.cleaned_data.get('item_price')
        if item_price <= 0:
            raise forms.ValidationError("Il prezzo deve essere maggiore di 0")
        return item_price

    def clean(self):
        cleaned_data = super().clean()
        item_name = cleaned_data.get('item_name')
        item_price = cleaned_data.get('item_price')
        item_desc = cleaned_data.get('item_desc')
        if "pizza" in item_name.lower():
            if item_price is not None and item_price < 10:
                raise forms.ValidationError("Il prezzo della pizza deve essere maggiore di 10")
        if item_desc is not None and item_name is not None \
            and item_desc.lower().strip() == item_name.lower().strip():
                self.add_error('item_desc', 
                "La descrizione del prodotto deve essere diversa dal nome")
        return cleaned_data