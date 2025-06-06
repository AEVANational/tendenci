from datetime import datetime, timedelta
import time as ttime

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.utils.translation import ngettext
from django.contrib import messages
from django.contrib.admin import SimpleListFilter
from django.http import StreamingHttpResponse

from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.perms.utils import update_perms_and_save
from tendenci.apps.profiles.models import Profile
from tendenci.apps.profiles.forms import ProfileAdminForm
from tendenci.apps.profiles.utils import iter_users


class ProfileAdmin(TendenciBaseModelAdmin):
    list_display = ('username', 'account_id', 'first_name', 'last_name', 'get_email', 'is_active', 'is_superuser', 'get_last_login')
    search_fields = ('account_id', 'display_name', 'user__first_name', 'user__last_name', 'user__username', 'user__email')

    fieldsets = (
        (_('Name Information'), {'fields': ('salutation',
                                            'first_name',
                                            'initials',
                                            'last_name',
                                            'position_title',
                                            'display_name',
                                            'hide_in_search',)}),
        (_('Phone Information'), {'fields': ('phone',
                                             'phone2',
                                             'fax',
                                             'work_phone',
                                             'home_phone',
                                             'mobile_phone',
                                             'hide_phone',)}),
        (_('E-mail and Internet Information'), {'fields': ('email',
                                                           'email2',
                                                           'url',
                                                           'hide_email',)}),
        (_('Company Information'), {'fields': ('company',
                                               'department',)}),
        (_('Address Information'), {'fields': ('mailing_name',
                                               'address',
                                               'address2',
                                               'city',
                                               'state',
                                               'zipcode',
                                               'country',
                                               'hide_address',)}),
        (_('Alternate Address Information'), {'fields': ('address_2',
                                               'address2_2',
                                               'city_2',
                                               'state_2',
                                               'zipcode_2',
                                               'country_2',)}),
        (_('Login Information'), {'fields': ('username',
                                             'password1',
                                             'password2',
                                             'interactive',
                                             'status_detail',)}),
        (_('Notes'), {'fields': ('notes',)}),
        (_('Optional Information'), {'fields': ('time_zone',
                                                'language',
                                                'spouse',
                                                'dob',
                                                'sex',)}),
        (_('Administrator Information'), {'fields': ('account_id',
                                                     'admin_notes',
                                                     'security_level',)}),)
    form = ProfileAdminForm

    ordering = ('user__last_name', 'user__first_name')

    def get_object(self, request, object_id, from_field=None):
        obj = super(ProfileAdmin, self).get_object(request, object_id, from_field=from_field)
        # Avoid language being accidentally set to the first option 'ar'
        # because en-us is not an option in the language dropdown
        if obj and obj.language == 'en-us':
            obj.language = 'en'
        return obj

    def save_model(self, request, object, form, change):
        instance = form.save(request=request, commit=False)
        instance = update_perms_and_save(request, form, instance, log=False)

        log_defaults = {
            'instance': object,
            'action': "edit"
        }
        if not change:
            log_defaults['action'] = "add"

        EventLog.objects.log(**log_defaults)
        return instance

    def save_form(self, request, form, change):
        return form.save(request=request, commit=False)

    def get_email(self, obj):
        return obj.user.email

    get_email.admin_order_field = 'user__email'
    get_email.short_description = _('Email')

    def is_superuser(self, obj):
        return obj.is_superuser
    is_superuser.boolean = True

    def is_active(self, obj):
        return obj.is_active
    is_active.boolean = True

    def get_last_login(self, obj):
        return obj.user.last_login
    get_last_login.short_description = _('Last Login')

    def get_user(self, obj):
        name = "%s %s" % (obj.user.first_name, obj.user.last_name)
        name = name.strip()

        return name or obj.user.username
    get_user.short_description = _('User')

admin.site.register(Profile, ProfileAdmin)


class LastLoginFilter(SimpleListFilter):
    title = 'Last Login'
    parameter_name = 'last_login'

    def lookups(self, request, model_admin):
        return (
            (1, '1 year ago'),
            (5, '5 years ago'),
            (10, '10 years ago'),
            (999, 'Never Logged in'),
        )

    def queryset(self, request, queryset):
        try:
            value = int(self.value())
        except:
            value = None

        if value is None:
            return queryset

        if value == 999:
            queryset = queryset.filter(last_login__isnull=True)
        else:
            dt = datetime.now() - timedelta(days=365 * value)
            queryset = queryset.filter(last_login__lt=dt)

            #print(queryset.query)
        return queryset


def export_selected_users(modeladmin, request, queryset):
    """
    Exports the selected users.
    """
    response = StreamingHttpResponse(
    streaming_content=(iter_users(queryset)),
    content_type='text/csv',)
    response['Content-Disposition'] = f'attachment;filename=users_export_{ttime.time()}.csv'
    return response


class MyUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name',
                    'show_member_number', 'is_staff', 'is_superuser', 'is_active', 'last_login')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        # Removing the permission part
        # (_('Permissions'), {'fields': ('is_staff', 'is_active', 'is_superuser', 'user_permissions')}),
        (_('Permissions'), {'fields': ('user_permissions',)}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_filter = ("is_staff", "is_superuser", "is_active", LastLoginFilter)
    ordering = ('-id',)
    actions = [
        export_selected_users
    ]
    
    def show_member_number(self, instance):
        [member_number] = Profile.objects.filter(user=instance).values_list('member_number', flat=True)[:1] or ['']
        return member_number

    def has_delete_permission(self, request, obj=None):
        result = super(MyUserAdmin, self).has_delete_permission(request, obj=obj)

        if obj:
            num_rps = obj.recurring_payments.filter(status=True, status_detail='active').count()
            if num_rps > 0:
                self.message_user(request, ngettext(
                    f'This user "{obj}" has {num_rps} recurrent payment associated with, it cannot be deleted.',
                    f'This user "{obj}" has {num_rps} recurrent payments associated with, it cannot be deleted.',
                    num_rps,
                ), messages.ERROR)
                return False
        return result

    show_member_number.short_description = 'Member number'
    show_member_number.admin_order_field = 'profile__member_number'

admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)
