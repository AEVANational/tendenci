import datetime

from django import forms
from django.forms.widgets import SelectDateWidget
from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string
from django.conf import settings
from django_q.tasks import schedule

from tendenci.apps.emails.models import Email
from tendenci.apps.site_settings.utils import get_setting
#from tendenci.apps.campaign_monitor.models import Template
from tendenci.apps.newsletters.utils import get_type_choices, is_newsletter_relay_set, get_default_template_choices
from tendenci.apps.newsletters.models import NewsletterTemplate, Newsletter
from tendenci.apps.newsletters.models import (
    THIS_YEAR,
    DAYS_CHOICES,
    INCLUDE_CHOICES
)
from tendenci.apps.perms.utils import get_query_filters, get_groups_query_filters
from tendenci.apps.user_groups.models import Group
from tendenci.apps.base.forms import FormControlWidgetMixin

EMAIL_SEARCH_CRITERIA_CHOICES = (
    ('subject__icontains', _('Subject')),
    ('id', _('Email ID #')),
    ('sender__icontains', _('Sender')),
    ('body__icontains', _('Body of Email')),
    ('owner__id', _('Owner User ID #')),
    ('owner_username', _('Owner Username')),
    ('creator__id', _('Creator User ID #')),
    ('creator_username', _('Creator Username'))
)


# class TemplateForm(forms.ModelForm):
#     class Meta:
#         model = Template
#         exclude = ["template_id", "create_date", "update_date", "cm_preview_url", "cm_screenshot_url"]
#
#     zip_file = forms.FileField(required=False)


class GenerateForm(forms.Form):
    # module content
    jump_links = forms.ChoiceField(initial=1, choices=INCLUDE_CHOICES)
    events =  forms.ChoiceField(initial=1, choices=INCLUDE_CHOICES)
    event_start_dt = forms.DateField(initial=datetime.date.today(), widget=SelectDateWidget(None, list(range(1920, THIS_YEAR+10))))
    event_end_dt = forms.DateField(initial=datetime.date.today() + datetime.timedelta(days=90), widget=SelectDateWidget(None, list(range(1920, THIS_YEAR+10))))
    events_type = forms.ChoiceField(initial='', choices=(), required=False)
    articles = forms.ChoiceField(initial=1, choices=INCLUDE_CHOICES)
    articles_days = forms.ChoiceField(initial=60, choices=DAYS_CHOICES)
    news = forms.ChoiceField(initial=1, choices=INCLUDE_CHOICES)
    news_days = forms.ChoiceField(initial=30, choices=DAYS_CHOICES)
    jobs = forms.ChoiceField(initial=1, choices=INCLUDE_CHOICES)
    jobs_days = forms.ChoiceField(initial=30, choices=DAYS_CHOICES)
    pages = forms.ChoiceField(initial=0, choices=INCLUDE_CHOICES)
    pages_days = forms.ChoiceField(initial=7, choices=DAYS_CHOICES)

    #Campaign Monitor Template
    template = forms.ModelChoiceField(queryset=NewsletterTemplate.objects.all())

    def __init__(self, *args, **kwargs):
        super(GenerateForm, self).__init__(*args, **kwargs)
        self.fields['events_type'].choices = get_type_choices()

class OldGenerateForm(forms.ModelForm):
    default_template = forms.ChoiceField(widget=forms.RadioSelect, choices=())
    class Meta:
        model = Newsletter
        fields = "__all__"
        exclude = ["enforce_direct_mail_flag"]
        widgets = {
            'subject': forms.TextInput(attrs={'size': 50}),
            'event_start_dt': SelectDateWidget(None, list(range(THIS_YEAR-1, THIS_YEAR+10))),
            'event_end_dt': SelectDateWidget(None, list(range(THIS_YEAR-1, THIS_YEAR+10))),
            'format': forms.RadioSelect
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(OldGenerateForm, self).__init__(*args, **kwargs)
        not_required = ['actionname', 'actiontype', 'article', 'send_status',
        'date_created', 'date_submitted', 'date_email_sent', 'email_sent_count',
        'date_last_resent', 'resend_count']
        self.fields['default_template'].blank = False
        self.fields['default_template'].choices = get_default_template_choices()
        self.fields['email'].required = False
        self.fields['group'].empty_label = _('SELECT ONE')
        self.fields['event_start_dt'].initial = datetime.date.today()
        self.fields['event_end_dt'].initial = datetime.date.today() + datetime.timedelta(days=30)
        
        default_groups = Group.objects.filter(status=True, status_detail="active",
                                              sync_newsletters=True)
        if not self.request.user.is_superuser:
            if get_setting('module', 'user_groups', 'permrequiredingd') == 'change':
                filters = get_groups_query_filters(self.request.user,)
                default_groups = default_groups.filter(filters).distinct()
        self.fields['group'].queryset = default_groups

        for key in not_required:
            self.fields[key].required = False

    def clean_group(self):
        data = self.cleaned_data
        group = data.get('group', None)
        member_only = data.get('member_only', False)

        if not member_only and not group:
            raise forms.ValidationError(_('Usergroup field is required if Send to members only is unchecked.'))

        return group

    def save(self, *args, **kwargs):
        data = self.cleaned_data
        subject = ''
        subj = data.get('subject', '')
        inc_last_name = data.get('personalize_subject_last_name')
        inc_first_name = data.get('personalize_subject_first_name')

        if inc_first_name and not inc_last_name:
            subject = '[firstname] ' + subj
        elif inc_last_name and not inc_first_name:
            subject = '[lastname] ' + subj
        elif inc_first_name and inc_last_name:
            subject = '[firstname] [lastname] ' + subj
        else:
            subject = subj
        nl = super(OldGenerateForm, self).save(*args, **kwargs)
        nl.subject = subject
        nl.actionname = subject
        nl.date_created = datetime.datetime.now()
        nl.send_status = 'draft'
        if nl.default_template:
            template = render_to_string(template_name=nl.default_template, request=self.request)
            email_content = nl.generate_newsletter(self.request, template)

            email = Email()
            email.subject = subject
            email.body = email_content
            email.sender = get_setting('site', 'global', 'siteemailnoreplyaddress')
            email.sender_display = self.request.user.profile.get_name()
            email.reply_to = self.request.user.email
            email.creator = self.request.user
            email.creator_username = self.request.user.username
            email.owner = self.request.user
            email.owner_username = self.request.user.username
            email.save()
            nl.email = email

        nl.save()

        return nl


class MarketingStepOneForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields= ('actiontype', 'actionname',)

    def __init__(self, *args, **kwargs):
        super(MarketingStepOneForm, self).__init__(*args, **kwargs)
        self.fields['actiontype'].required = True
        self.fields['actionname'].required = True


class MarketingStepThreeForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ('member_only', 'group',)

    def clean_group(self):
        data = self.cleaned_data
        group = data.get('group', None)
        member_only = data.get('member_only', False)

        if not member_only and not group:
            raise forms.ValidationError(_('Usergroup field is required if Send to members only is unchecked.'))

        return group


class MarketingStepFourForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ('subject', 'send_to_email2', 'enforce_direct_mail_flag', 'sla', 'member_only', 'group')

    def __init__(self, *args, **kwargs):
        super(MarketingStepFourForm, self).__init__(*args, **kwargs)
        self.fields['sla'].required = True

        self.fields['send_to_email2'] = forms.ChoiceField(
            choices=(
                (True, _('Yes')),
                (False, _('No')),
                ),
            label=_('include emal2'))
        self.fields['enforce_direct_mail_flag'].widget = forms.Select(choices=(
                (True, _('Yes')),
                (False, _('No')),
                ),)

    def clean_group(self):
        data = self.cleaned_data
        group = data.get('group', None)
        member_only = data.get('member_only', False)

        if not member_only and not group:
            raise forms.ValidationError(_('Usergroup field is required if Send to members only is unchecked.'))

        return group


class MarketingStepFiveForm(FormControlWidgetMixin, forms.ModelForm):
    create_article = forms.BooleanField(label=_('Create an Article from this Newsletter?'), required=False)
    schedule_send = forms.BooleanField(label=_('Schedule to Send?'), required=False)
    schedule_send_dt = forms.SplitDateTimeField(label=_('Starts On'), required=False,
                                  input_date_formats=['%Y-%m-%d', '%m/%d/%Y'],
                                  input_time_formats=['%I:%M %p', '%H:%M:%S'])
    class Meta:
        model = Newsletter
        fields = ('create_article',
                  'schedule_send',
                  'schedule_send_dt',
                  'schedule_type',
                  'repeats',
                  'send_status',)

    def __init__(self, *args, **kwargs):
        super(MarketingStepFiveForm, self).__init__(*args, **kwargs)
        if not settings.NEWSLETTER_SCHEDULE_ENABLED:
            self.fields.pop('schedule_send')
            self.fields.pop('schedule_send_dt')
            self.fields.pop('schedule_type')
            self.fields.pop('repeats')
        else:
            self.fields['schedule_send_dt'].initial = datetime.datetime.now() + datetime.timedelta(days=1)

    def clean_schedule_send_dt(self):
        schedule_send_dt = self.cleaned_data['schedule_send_dt']
        if schedule_send_dt and schedule_send_dt < datetime.datetime.now() + datetime.timedelta(minutes=1):
            raise forms.ValidationError(_('Please select a time at least 5 minutes from now'))
        return schedule_send_dt

    def clean(self):
        data = self.cleaned_data

        # check if email host relay is properly set up
        if not is_newsletter_relay_set():
            raise forms.ValidationError(_('Email relay is not configured properly.'
                                            ' Newsletter cannot be sent.'))
        if 'schedule_send' in data and data['schedule_send']:
            if not 'schedule_send_dt' in data or not data['schedule_send_dt']:
                raise forms.ValidationError(_("You've checked Schedule to Send, please also pick a date and time to send."))
            if not 'schedule_type' in data or not data['schedule_type']:
                raise forms.ValidationError(_("Please select Frequency."))

        return data

    def save(self, *args, **kwargs):
        create_article = self.cleaned_data.get('create_article', False)
        newsletter = super(MarketingStepFiveForm, self).save(*args, **kwargs)
        newsletter.date_submitted = datetime.datetime.now()
        if newsletter.schedule_type == 'O':
            newsletter.repeats = 0
        newsletter.save()

        if create_article:
            newsletter.generate_article(newsletter.email.creator)

        schedule_send = self.cleaned_data.get('schedule_send', False)
        if not schedule_send:
            # not scheduled - send immediately
            newsletter.send_to_recipients()
        else:
            # make a schedule
            repeats = newsletter.repeats
            if repeats == 0:
                # set it to 1 otherwise django-q wont run
                repeats = 1
            s = schedule(
                    'django.core.management.call_command',
                    'send_newsletter',
                    newsletter.id,
                    schedule_type=newsletter.schedule_type,
                    next_run=newsletter.schedule_send_dt,
                    repeats=repeats)
            newsletter.schedule = s
            newsletter.save()

        return newsletter


class MarketingEditScheduleForm(FormControlWidgetMixin, forms.ModelForm):
    schedule_send_dt = forms.SplitDateTimeField(label=_('Starts On'),
                                  input_date_formats=['%Y-%m-%d', '%m/%d/%Y'],
                                  input_time_formats=['%I:%M %p', '%H:%M:%S'])
    class Meta:
        model = Newsletter
        fields = ('schedule_send_dt',
                  'schedule_type',
                  'repeats',)

    def clean_schedule_send_dt(self):
        schedule_send_dt = self.cleaned_data['schedule_send_dt']
        if schedule_send_dt and schedule_send_dt < datetime.datetime.now() + datetime.timedelta(minutes=1):
            raise forms.ValidationError(_('Please select a time at least 5 minutes from now'))
        return schedule_send_dt

    def save(self, *args, **kwargs):
        newsletter = super(MarketingEditScheduleForm, self).save(*args, **kwargs)
        if newsletter.schedule_type == 'O':
            newsletter.repeats = 0
        newsletter.save()

        # update a schedule
        repeats = newsletter.repeats
        if repeats == 0:
            # set it to 1 otherwise django-q wont run
            repeats = 1
        if newsletter.schedule:
            s = newsletter.schedule
            s.schedule_type = newsletter.schedule_type
            s.next_run = newsletter.schedule_send_dt
            s.repeats = repeats
            s.save()
        else:
            s = schedule(
                    'django.core.management.call_command',
                    'send_newsletter',
                    newsletter.id,
                    schedule_type=newsletter.schedule_type,
                    next_run=newsletter.schedule_send_dt,
                    repeats=repeats)
            newsletter.schedule = s
            newsletter.save()

        return newsletter


class NewslettterEmailUpdateForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ('email',)


class MarketingStep2EmailFilterForm(forms.Form):
    search_criteria = forms.ChoiceField(choices=EMAIL_SEARCH_CRITERIA_CHOICES)
    q = forms.CharField(required=False)

    def filter_email(self, request, queryset):
        search_criteria = request.GET.get('search_criteria')
        q = request.GET.get('q')
        query = {search_criteria: q}
        queryset = queryset.filter(**query)

        return queryset
