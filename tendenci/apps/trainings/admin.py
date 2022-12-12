from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.urls import reverse

from .models import (SchoolCategory, Certification,
                     CertCat, Course, Transcript,
                     TeachingActivity,
                     OutsideSchool)
from .forms import CourseForm


class TeachingActivityAdmin(admin.ModelAdmin):
    model = TeachingActivity
    list_display = ['id',
                    'user',
                    'activity_name',
                    'date',
                    'status_detail',]
    list_editable = ('status_detail', )
    search_fields = ['activity_name',
                     'user__first_name',
                     'user__last_name',
                     'user__email']
    list_filter = ['status_detail',]
    fieldsets = (
        (None, {
            'fields': (
            'user',
            'activity_name',
            'status_detail',
            'date',
            'description',
            
        )},),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing
            return self.readonly_fields + ('user',)
        return self.readonly_fields


class OutsideSchoolAdmin(admin.ModelAdmin):
    model = OutsideSchool
    list_display = ['id',
                    'user',
                    'school_name',
                    'school_category',
                    'credits',
                    'certification_track',
                    'date',
                    'status_detail',]
    list_editable = ('school_category', 'credits', 'certification_track', 'status_detail', )
    search_fields = ['school_name',
                     'user__first_name',
                     'user__last_name',
                     'user__email']
    list_filter = ['status_detail',]
    #form = OutsideSchoolAdminForm
    fieldsets = (
        (None, {
            'fields': (
            'user',
            'school_name',
            'school_category',
            'date',
            'credits',
            'certification_track',
            'status_detail',
            'description',
            
        )},),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing
            return self.readonly_fields + ('user',)
        return self.readonly_fields


class SchoolCategoryAdmin(admin.ModelAdmin):
    model = SchoolCategory
    list_display = ['id', 'name',
                    'status_detail',]


class CategoryAdminInline(admin.TabularInline):
    fieldsets = (
        (None, {
            'fields': (
            'category',
            'required_credits'
        )},),
    )
    extra = 0
    model = CertCat


class CertificationAdmin(admin.ModelAdmin):
    model = SchoolCategory
    list_display = ['id', 'name',
                    'period', 'enable_diamond']
    inlines = (CategoryAdminInline,)
    fieldsets = (
        (_(''), {
            'fields': ('name',
                       'period',
                       'enable_diamond',)
        }),
        (_('Diamond Requirements'), {'description':
                                     'Set requirements for each diamond',
                                     'classes': ('collapse',),
                                     'fields': (
            'diamond_name',
            'diamond_required_credits',
            'diamond_required_online_credits',
            'diamond_period',
            'diamond_required_activity'
        )}),)


class CourseAdmin(admin.ModelAdmin):
    model = Course
    list_display = ['id', 'name',
                    'location_type',
                    'school_category',
                    'status_detail'
                    ]
    search_fields = ['name', 'location_type']
    list_filter = ['status_detail', 'location_type', 'school_category']
    fieldsets = (
        (_('General'), {
            'fields': ('name',
                       'location_type',
                       'school_category',
                       'course_code',
                       'summary',
                       'description',
                       'credits',
                       'min_score',
                       'status_detail',)
        }),
        (_('Permissions'), {'classes': ('collapse',), 'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
        )}),
        )
    form = CourseForm


# class ExamAdmin(admin.ModelAdmin):
#     model = Exam
#     list_display = ['id', 'user',
#                     'course',
#                     'grade',
#                     'update_dt'
#                     ]
#     fieldsets = (
#         (None, {
#             'fields': (
#             'user',
#             'course',
#             'grade',
#         )},),
#     )


class TranscriptAdmin(admin.ModelAdmin):
    model = Transcript
    list_display = ['id', 'show_user', 'course', 'show_school',
                    'school_category',
                    'location_type',
                    'credits',
                    'certification_track',
                    'status', 
                    ]
    fieldsets = (
        (None, {
            'fields': (
            'user',
            'school_category',
            'location_type',
            'credits',
            'certification_track',
            'status',
        )},),
    )
    list_editable = ('status', )

    def has_add_permission(self, request):
        return False

    @mark_safe
    def show_school(self, instance):
        if instance.registrant_id:
            from tendenci.apps.events.models import Registrant
            [registrant] = Registrant.objects.filter(id=instance.registrant_id)[:1] or [None]
            if registrant:
                event = registrant.registration.event
                return '<a href="{0}" title="{1}">{1}</a>'.format(
                        reverse('event', args=[event.id]),
                        event.title,
                    )
        return ""
    show_school.short_description = 'School'

    # def show_course(self, instance):
    #     if instance.registrant_id:
    #         from tendenci.apps.events.models import Registrant
    #         [registrant] = Registrant.objects.filter(id=instance.registrant_id)[:1] or [None]
    #         if registrant:
    #             event = registrant.registration.event
    #             course = event.course
    #             return course.name
    #     return ""
    # show_course.short_description = 'Course'
    
    @mark_safe
    def show_user(self, instance):
        if instance.user:
            name = instance.user.get_full_name()
            if not name:
                name = instance.user.username
            return '<a href="{0}" title="{1}">{1}</a>'.format(
                    reverse('profile', args=[instance.user.username]),
                    name
                )
        return ""
    show_user.short_description = 'User'
    show_user.admin_order_field = 'user__first_name'


admin.site.register(SchoolCategory, SchoolCategoryAdmin)
admin.site.register(Certification, CertificationAdmin)
admin.site.register(Course, CourseAdmin)
# admin.site.register(Exam, ExamAdmin)
admin.site.register(Transcript, TranscriptAdmin)
admin.site.register(TeachingActivity, TeachingActivityAdmin)
admin.site.register(OutsideSchool, OutsideSchoolAdmin)
