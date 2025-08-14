from django import forms
from .models import Event





class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'thumbnail', 'location']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',  # Enables the browser calendar picker
                'class': 'border rounded px-3 py-2 w-full focus:outline-none focus:ring focus:ring-pink-300'
            }),
            'description': forms.Textarea(attrs={
                'class': 'border rounded px-3 py-2 w-full focus:outline-none focus:ring focus:ring-pink-300'
            }),
            'thumbnail': forms.ClearableFileInput(attrs={
                'class': 'border rounded px-3 py-2 w-full focus:outline-none focus:ring focus:ring-pink-300'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in self.Meta.widgets:  # already handled in widgets
                field.widget.attrs.update({
                    'class': 'border rounded px-3 py-2 w-full focus:outline-none focus:ring focus:ring-pink-300'
                })



