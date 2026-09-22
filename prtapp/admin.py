from django.contrib import admin
from .models import Idea, Student, Investor


@admin.register(Idea)
class IdeaAdmin(admin.ModelAdmin):
    list_display = ("title", "name", "category", "stage", "college", "created_at")
    list_filter = ("category", "stage")
    search_fields = ("title", "name", "college", "description")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "college", "skill", "created_at")
    search_fields = ("name", "college", "phone", "email")


@admin.register(Investor)
class InvestorAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "occupation", "interest_area", "created_at")
    search_fields = ("name", "occupation", "phone", "email")

    # Is code ko admin.py ke bilkul niche add karein
from .models import ConnectionRequest

@admin.register(ConnectionRequest)
class ConnectionRequestAdmin(admin.ModelAdmin):
    list_display = ('investor', 'get_idea_title', 'get_student_name', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('investor__name', 'idea__title', 'idea__name')
    list_editable = ('status',) # Aap admin panel ki table se hi status direct badal sakti hain!

    # Idea ka title table mein dikhane ke liye helper function
    def get_idea_title(self, obj):
        return obj.idea.title
    get_idea_title.short_description = 'Idea Title'

    # Student ka naam table mein dikhane ke liye helper function
    def get_student_name(self, obj):
        return obj.idea.name
    get_student_name.short_description = 'Student Name'
