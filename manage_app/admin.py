from django.contrib import admin

# Register your models here.
from manage_app.models import track, series

admin.site.register(track)
admin.site.register(series)