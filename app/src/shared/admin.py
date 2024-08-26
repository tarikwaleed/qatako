from django.contrib import admin
from .models import CommandException,Feedings

class FeedingsAdmin(admin.ModelAdmin):

    readonly_fields = ('app','feeder','last_fed')

admin.site.register(CommandException)
admin.site.register(Feedings,FeedingsAdmin)
