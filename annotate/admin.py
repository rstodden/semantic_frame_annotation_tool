from django.contrib import admin

# Register your models here.
from .models import CoreElementType, FrameType, Comment, LoggedInUser, ExtendedUser, Frame, Slot, Sentence, Token, MWE

admin.site.register(CoreElementType)
admin.site.register(FrameType)
admin.site.register(Comment)
admin.site.register(LoggedInUser)
admin.site.register(ExtendedUser)
admin.site.register(Frame)
admin.site.register(MWE)
admin.site.register(Slot)
admin.site.register(Sentence)
admin.site.register(Token)