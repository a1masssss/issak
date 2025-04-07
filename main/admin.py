from django.contrib import admin
from main.models import PDFDocument, SummaryNotes, Video
from users.models import User, EmailActivation

@admin.register(PDFDocument)
class PDFDocumentAdmin(admin.ModelAdmin):
    list_display = ('file', 'uploaded_at')  # Fields shown in the list
    search_fields = ('file',)  # Searchable fields
    list_filter = ('uploaded_at',)

@admin.register(SummaryNotes)
class SummaryNotesAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at')
    search_fields = ('title', 'user__username')
    list_filter = ('created_at',)

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('url', 'uploaded_at')
    search_fields = ('url',)
    list_filter = ('uploaded_at',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'date_joined', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('first_name', 'last_name', 'email', )
    list_filter = ('is_active', 'date_joined', )

@admin.register(EmailActivation)
class EmailActivationAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active', 'token')
    search_fields = ('user', )
    list_filter = ('is_active', )

