from django.contrib import admin
from models import General, Specific, User, GeneralVote, SpecificVote, Facet, SpecificFacet
# Register your models here.
admin.site.register(General)
admin.site.register(Specific)
admin.site.register(User)
admin.site.register(GeneralVote)
admin.site.register(SpecificVote)
admin.site.register(Facet)
admin.site.register(SpecificFacet)
