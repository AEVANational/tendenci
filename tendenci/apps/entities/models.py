import uuid

from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from tendenci.apps.entities.managers import EntityManager


class Entity(models.Model):
    ENTITY_TYPES = (
        ('', _('SELECT ONE')),
        ('Committee', _('Committee')),
        ('Chapter', _('Chapter')),
        ('Reporting', _('Reporting')),
        ('Study Group', _('Study Group')),
        ('Directory', _('Directory')),
        ('Corporate Membership', _('Corporate Membership')),
        ('Membership', _('Membership')),
        ('Technical Interest Group', _('Technical Interest Group')),
        ('Other', _('Other')),
    )
    guid = models.CharField(max_length=40)
    entity_name = models.CharField(_('Name'), max_length=200, blank=True)
    entity_type = models.CharField(_('Type'), choices=ENTITY_TYPES, max_length=200, blank=True, default="Reporting")
    #entity_parent_id = models.IntegerField(_('Parent ID'), default=0)
    entity_parent = models.ForeignKey('self', related_name='entity_children', null=True, blank=True,
                                      on_delete=models.SET_NULL)
    # contact info
    contact_name = models.CharField(_('Contact Name'), max_length=200, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    fax = models.CharField(max_length=50, blank=True)
    email = models.CharField(max_length=120, blank=True)
    website = models.CharField(max_length=300, blank=True)
    summary = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    admin_notes = models.TextField(_('Admin Notes'), blank=True)
    
    show_for_donation = models.BooleanField(_('Use for Donation Allocation'), default=False,
            help_text=_('If checked, it will appear as an option for donation allocation on the donation form.'),)
    #donation_default_amount = models.CharField(max_length=30, blank=True, default='',
    #                                            help_text=_('Comma separated. Example for multiple amounts, 2500,5000'))

    # Model removed from TendenciBaseModel. Those fields added below
    allow_anonymous_view = models.BooleanField(_("Public can view"), default=True)
    allow_user_view = models.BooleanField(_("Signed in user can view"), default=True)
    allow_member_view = models.BooleanField(default=True)
    allow_anonymous_edit = models.BooleanField(default=False)
    allow_user_edit = models.BooleanField(_("Signed in user can change"), default=False)
    allow_member_edit = models.BooleanField(default=False)

    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, related_name="%(class)s_creator", editable=False, null=True, on_delete=models.SET_NULL)
    creator_username = models.CharField(max_length=150)
    owner = models.ForeignKey(User, related_name="%(class)s_owner", null=True, on_delete=models.SET_NULL)
    owner_username = models.CharField(max_length=150)
    status = models.BooleanField("Active", default=True)
    status_detail = models.CharField(max_length=50, default='active')

    objects = EntityManager()

    class Meta:
#         permissions = (("view_entity", _("Can view entity")),)
        verbose_name_plural = _("entities")
        ordering = ("entity_name",)
        app_label='entities'

    def get_absolute_url(self):
        return reverse('entity', args=[self.pk])

    def __str__(self):
        return self.entity_name

    def save(self, *args, **kwargs):
        if not self.guid:
            self.guid = str(uuid.uuid4())

        super(Entity, self).save(*args, **kwargs)

    @staticmethod
    def get_search_filter(user):
        from tendenci.apps.perms.utils import has_perm
        if user.profile.is_superuser or has_perm(user, 'entities.view_entity'):
            return None

        if user.is_authenticated:
            creator_owner_q = (Q(creator=user) | Q(owner=user))
            if user.profile.is_member:
                return  Q(status=True) & Q(status_detail='active') & ((Q(allow_member_view=True) | Q(allow_user_view=True) | Q(allow_anonymous_view=True)) | creator_owner_q)
            else:
                return  Q(status=True) & Q(status_detail='active') & ((Q(allow_user_view=True) | Q(allow_anonymous_view=True)) | creator_owner_q)
        else:
            return Q(status=True) & Q(status_detail='active') & Q(allow_anonymous_view=True)

