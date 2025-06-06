import uuid
from datetime import datetime
from decimal import Decimal

import stripe

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models.signals import post_save
from django.conf import settings

from tendenci.apps.notifications import models as notification
from tendenci.apps.perms.utils import has_perm, get_notice_recipients
from tendenci.apps.invoices.managers import InvoiceManager
from tendenci.apps.invoices.listeners import update_profiles_total_spend
from tendenci.apps.accountings.utils import (
    make_acct_entries,
    make_acct_entries_reversing,
    make_acct_entries_initial_reversing,
    make_acct_entries_refund
)
from tendenci.apps.entities.models import Entity
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.payments.stripe.models import StripeAccount
from tendenci.apps.regions.models import Region


STATUS_DETAIL_CHOICES = (
    ('estimate', _('Estimate')),
    ('tendered', _('Tendered')))


class Invoice(models.Model):
    class LineDescriptions:
        CANCELLATION_FEE = _('Cancellation fee (to be deducted from refunds)')
        REFUND = _('Refund')

    guid = models.CharField(max_length=50)

    object_type = models.ForeignKey(ContentType, blank=True, null=True, on_delete=models.CASCADE)
    object_id = models.IntegerField(default=0, blank=True, null=True)
    _object = GenericForeignKey('object_type', 'object_id')
    title = models.CharField(max_length=200, blank=True, null=True)
    creator = models.ForeignKey(User, related_name="invoice_creator", null=True, on_delete=models.SET_NULL)
    creator_username = models.CharField(max_length=150, null=True)
    owner = models.ForeignKey(User, related_name="invoice_owner", null=True, on_delete=models.SET_NULL)
    owner_username = models.CharField(max_length=150, null=True)
    entity = models.ForeignKey(Entity, blank=True, null=True, default=None, on_delete=models.SET_NULL, related_name="invoices")
    create_dt = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    update_dt = models.DateTimeField(auto_now=True)
    tender_date = models.DateTimeField(null=True)
    void_date = models.DateTimeField(null=True)
    voided_by = models.ForeignKey(User, related_name="invoice_voided_by", null=True, on_delete=models.SET_NULL)
    void_reason = models.TextField(_('Reason to void'), max_length=200, blank=True, default='')
    arrival_date_time = models.DateTimeField(blank=True, null=True)
    is_void = models.BooleanField(default=False)
    status_detail = models.CharField(max_length=50, choices=STATUS_DETAIL_CHOICES, default='estimate')
    status = models.BooleanField(default=True)
    payments_credits = models.DecimalField(max_digits=15, decimal_places=2, blank=True, default=0)
    balance = models.DecimalField(max_digits=15, decimal_places=2, blank=True, default=0)
    total = models.DecimalField(max_digits=15, decimal_places=2, blank=True)
    refunds = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    adjusted_cancellation_fees = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    applied_cancellation_fees = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount_code = models.CharField(_('Discount Code'), max_length=100, blank=True, null=True)
    discount_amount = models.DecimalField(_('Discount Amount'), max_digits=10, decimal_places=2, default=0)
    variance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    variance_notes = models.TextField(max_length=1000, blank=True, null=True)
    receipt = models.BooleanField(default=False)
    gift = models.BooleanField(default=False)
    greeting = models.CharField(max_length=500, blank=True, null=True)
    instructions = models.CharField(max_length=500, blank=True, null=True)
    po = models.CharField(max_length=50, blank=True)
    terms = models.CharField(max_length=50, blank=True)
    disclaimer = models.CharField(max_length=150, blank=True, null=True)
    admin_notes = models.TextField(blank=True, null=True)
    fob = models.CharField(max_length=50, blank=True, null=True)
    project = models.CharField(max_length=50, blank=True, null=True)
    other = models.CharField(max_length=120, blank=True, null=True)
    message = models.CharField(max_length=150, blank=True, null=True)
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, blank=True)
    gratuity = models.DecimalField(blank=True, default=0, max_digits=6, decimal_places=4)
    tax_exempt = models.BooleanField(default=True)
    tax_exemptid = models.CharField(max_length=50, blank=True, null=True)
    tax_rate = models.FloatField(blank=True, default=0)
    tax_rate_2 = models.DecimalField(blank=True, max_digits=6, decimal_places=5, default=0)
    taxable = models.BooleanField(default=False)
    tax = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    tax_2 = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    tax_label_2 = models.CharField(max_length=6, blank=True, default='')
    region = models.ForeignKey(Region, blank=True, null=True, on_delete=models.SET_NULL)
    bill_to = models.CharField(max_length=120, blank=True)
    bill_to_first_name = models.CharField(max_length=100, blank=True, null=True)
    bill_to_last_name = models.CharField(max_length=100, blank=True, null=True)
    bill_to_company = models.CharField(max_length=100, blank=True, null=True)
    bill_to_address = models.CharField(max_length=250, blank=True, null=True)
    bill_to_city = models.CharField(max_length=50, blank=True, null=True)
    bill_to_state = models.CharField(max_length=50, blank=True, null=True)
    bill_to_zip_code = models.CharField(max_length=20, blank=True, null=True)
    bill_to_country = models.CharField(max_length=255, blank=True, null=True)
    bill_to_phone = models.CharField(max_length=50, blank=True, null=True)
    bill_to_fax = models.CharField(max_length=50, blank=True, null=True)
    bill_to_email = models.CharField(max_length=100, blank=True, null=True)
    ship_to = models.CharField(max_length=120, blank=True)
    ship_to_first_name = models.CharField(max_length=50, blank=True)
    ship_to_last_name = models.CharField(max_length=50, blank=True)
    ship_to_company = models.CharField(max_length=100, blank=True)
    ship_to_address = models.CharField(max_length=250, blank=True)
    ship_to_city = models.CharField(max_length=50, blank=True)
    ship_to_state = models.CharField(max_length=50, blank=True)
    ship_to_zip_code = models.CharField(max_length=20, blank=True)
    ship_to_country = models.CharField(max_length=255, blank=True)
    ship_to_phone = models.CharField(max_length=50, blank=True, null=True)
    ship_to_fax = models.CharField(max_length=50, blank=True, null=True)
    ship_to_email = models.CharField(max_length=100, blank=True, null=True)
    ship_to_address_type = models.CharField(max_length=50, blank=True, null=True)
    ship_date = models.DateTimeField()
    ship_via = models.CharField(max_length=50, blank=True)
    shipping = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    shipping_surcharge = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    box_and_packing = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    objects = InvoiceManager()

    class Meta:
#         permissions = (("view_invoice", _("Can view invoice")), )
        app_label = 'invoices'

    def __str__(self):
        return "Invoice %s" % self.pk

    def set_creator(self, user):
        """
        Sets creator fields.
        """
        self.creator = user
        self.creator_username = user.username

    def set_owner(self, user):
        """
        Sets owner fields.
        """
        self.owner = user
        self.owner_username = user.username

    def assign_tax(self, price_tax_rate_list, user, module_tax_rate_use_regions=False, corp_profile=None, region=None):
        """
        Calculate and assign tax to this invoice.
        
        If site uses regions for tax, 
        
        price_tax_rate_list is a list of (price, default_tax_rate) tuples,
        example: [(10.50, 0.0825), ..]
        """
        if not region:
            if module_tax_rate_use_regions or get_setting('module', 'invoices', 'taxrateuseregions'):
                if corp_profile:
                    region = corp_profile.region
                else:
                    if user and not user.is_anonymous and hasattr(user, 'profile'):
                        region = user.profile.region
        if region:
            # check if we need to use alternative region
            if get_setting('module', 'invoices', 'usealtregions') and \
                self.object_type and self.object_type.app_label not in ['corporate_memberships', 'memberships']:
                region_id = settings.ALTERNATIVE_REGIONS_MAP.get(region.id, region.id)
                if region_id != region.id:
                    region = Region.objects.filter(id=region_id).first() or region

            self.region = region
            self.tax_rate = region.tax_rate
            if region.tax_rate_2:
                self.tax_rate_2 = region.tax_rate_2
            if region.tax_label_2:
                self.tax_label_2 = region.tax_label_2
            for (price, _) in price_tax_rate_list:
                if price:
                    if self.tax_rate:
                        self.tax += self.tax_rate * price
                    if region.tax_rate_2:
                        self.tax_2 += self.tax_rate_2 * price
        else:
            for (price, default_tax_rate) in price_tax_rate_list:
                if price and default_tax_rate:
                    self.tax_rate = default_tax_rate
                    self.tax += self.tax_rate * price

        return self

    def bill_to_user(self, user):
        """
        This method populates all of the bill to fields
        via info in user and user.profile object.
        """
        self.bill_to = '%s %s' % (user.first_name, user.last_name)
        self.bill_to = self.bill_to.strip()

        self.bill_to_first_name = user.first_name
        self.bill_to_last_name = user.last_name
        self.bill_to_email = user.email

        if hasattr(user, 'profile'):
            profile = user.profile
            self.bill_to_company = profile.company
            self.bill_to_phone = profile.phone
            self.bill_to_fax = profile.fax
            if profile.is_billing_address or not profile.is_billing_address_2:
                self.bill_to_address = profile.address
                self.bill_to_city = profile.city
                self.bill_to_state = profile.state
                self.bill_to_zip_code = profile.zipcode
                self.bill_to_country = profile.country
            else:
                
                self.bill_to_address = profile.address_2
                self.bill_to_city = profile.city_2
                self.bill_to_state = profile.state_2
                self.bill_to_zip_code = profile.zipcode_2
                self.bill_to_country = profile.country_2

    def ship_to_user(self, user):
        """
        This method populates all of the ship to fields
        via info in user and user.profile object.
        """
        self.ship_to = '%s %s' % (user.first_name, user.last_name)
        self.ship_to = self.ship_to.strip()

        self.ship_to_first_name = user.first_name
        self.ship_to_last_name = user.last_name
        self.ship_to_email = user.email
        
        if hasattr(user, 'profile'):
            profile = user.profile
            self.ship_to_company = profile.company
            self.ship_to_phone = profile.phone
            self.ship_to_fax = profile.fax
            self.ship_to_address_type = profile.address_type
            if profile.is_billing_address or not profile.is_billing_address_2:
                self.ship_to_address = profile.address
                self.ship_to_city = profile.city
                self.ship_to_state = profile.state
                self.ship_to_zip_code = profile.zipcode
                self.ship_to_country = profile.country
            else:
                
                self.ship_to_address = profile.address_2
                self.ship_to_city = profile.city_2
                self.ship_to_state = profile.state_2
                self.ship_to_zip_code = profile.zipcode_2
                self.ship_to_country = profile.country_2

    def split_title(self):
        if ": " in self.title:
            split_title = ': '.join(self.title.split(': ')[1:])
            return u'%s' % split_title
        return self.title

    def get_absolute_url(self):
        return reverse('invoice.view', args=[self.id])

    def get_absolute_url_with_guid(self):
        return reverse('invoice.view', args=[self.id, self.guid])

    def get_discount_url(self):
        from tendenci.apps.discounts.models import Discount
        if self.discount_code:
            try:
                discount = Discount.objects.get(discount_code=self.discount_code)
                return discount.get_absolute_url
            except Discount.DoesNotExist:
                return ''
        return ''

    def save(self, user=None, *args, **kwargs):
        """
        Set guid, creator and owner if any of
        these fields are missing.
        """
        self.guid = self.guid or uuid.uuid4().hex

        if hasattr(user, 'pk') and not user.is_anonymous:
            self.set_creator(user)
            self.set_owner(user)

        # assign entity
        if not self.entity_id and self.object_type:
            self.entity = self.get_entity()

        self.verifydata()
        super(Invoice, self).save()

    def verifydata(self):
        # verify each field
        for field in Invoice._meta.fields:
            value = getattr(self, field.name)
            if field.max_length and value and len(value) > field.max_length:
                value = value[:field.max_length]
                setattr(self, field.name, value)

    def delete(self, *args, **kwargs):
        """
        Invoices are never deleted.
        Per Ed Schipul 06/05/2013
        """
        pass

    def get_entity(self):
        """
        Discover the entity for this invoice.

        Note that - the entity we're looking for is the entity
        from the object's group, not the object's entity field.
        """
        entity = None
        obj = self.get_object()
        if obj:
            # an object is associated with a group which ties to an entity
            group = None
            if hasattr(obj, 'group'):
                group = getattr(obj, 'group')
                if group:
                    entity = group.entity
        if not entity:
            entity = getattr(obj, 'entity', None) or Entity.objects.first()

        return entity

    def get_object(self):
        _object = None
        try:
            _object = self._object
        except:
            pass
        # exclude the soft deleted object - when an object is soft deleted,
        # its slug is appended with "@ + object.pk", which causes error on
        # resolving url (on invoice search and detail pages) because "@"
        # is not valid in the slug url pattern.
        if _object and hasattr(_object, 'status') and (not _object.status):
            _object = None
        return _object

    @property
    def use_third_party_payment(self):
        obj = self.get_object()
        if hasattr(obj, 'use_third_party_payment'):
            return getattr(obj, 'use_third_party_payment')
        return False

    @property
    def external_payment_link(self):
        obj = self.get_object()
        if hasattr(obj, 'external_payment_link'):
            return getattr(obj, 'external_payment_link')
        return ''

    def get_donation_amount(self):
        obj = self.get_object()
        if obj and hasattr(obj, 'donation_amount'):
            return obj.donation_amount
        return None

    def get_status(self):
        """
        Return status (string)
        Use status_detail and is_voide attribute
        """
        if self.is_void:
            return u'void'

        return self.status_detail

    @property
    def graguity_in_percentage(self):
        return '{:.1%}'.format(self.gratuity)

    @property
    def is_tendered(self):
        boo = False
        if self.id > 0:
            if self.status_detail.lower() == 'tendered':
                boo = True
        return boo

    def tender(self, user):
        """ mark it as tendered if we have records """
        if not self.is_tendered:
            # make accounting entry
            make_acct_entries(user, self, self.total)
            self.status_detail = 'tendered'
            self.status = 1
            self.tender_date = datetime.now()
            self.save()
        return True

    # if this invoice allows view by user2_compare
    def allow_view_by(self, user2_compare, guid=''):
        if user2_compare.profile.is_superuser:
            return True

        if has_perm(user2_compare, 'invoices.view_invoice'):
            return True

        if not get_setting("module", "invoices", "disallow_private_urls"):
            if self.guid == guid:
                return True

        obj = self.get_object()
        if obj and hasattr(obj, 'allow_adjust_invoice_by'):
            # example: chapter leaders can view/adjust invoices for their chapter memberships.
            if obj.allow_adjust_invoice_by(user2_compare):
                return True
        if obj and hasattr(obj, 'allow_view_invoice_by'):
            # example: corp reps can view the invoices of their corp memberships.
            if obj.allow_view_invoice_by(user2_compare):
                return True

        if user2_compare.is_authenticated:
            if user2_compare in [self.creator, self.owner] or \
                    (user2_compare.email and self.bill_to_email \
                     and user2_compare.email.lower() == self.bill_to_email.lower()):
                return self.status

        return False

    def allow_payment_by(self, user2_compare,  guid=''):
        return self.allow_view_by(user2_compare,  guid)

    # if this invoice allows edit by user2_compare
    def allow_edit_by(self, user2_compare):
        if not user2_compare.is_authenticated:
            return False

        if user2_compare.is_superuser:
            return True
        else:
            if user2_compare and user2_compare.id > 0:
                if has_perm(user2_compare, 'invoices.change_invoice'):
                    return True

                obj = self.get_object()
                if obj and hasattr(obj, 'allow_adjust_invoice_by'):
                    # example: chapter leaders can view/adjust invoices for their chapter memberships.
                    if obj.allow_adjust_invoice_by(user2_compare):
                        return True

#                 if self.creator == user2_compare or \
#                         self.owner == user2_compare or \
#                         self.bill_to_email == user2_compare.email:
#                     if self.status:
#                         # user can only edit a non-tendered invoice
#                         if not self.is_tendered:
#                             return True
#             else:
#                 if self.guid and self.guid == guid:  # for anonymous user
#                     if self.status and not self.is_tendered:
#                         return True
        return False

    def make_payment(self, user, amount):
        """
        Updates the invoice balance by adding
        accounting entries.
        """

        if self.is_tendered and self.balance > 0:
            self.balance -= amount
            self.payments_credits += amount
            self.save()

            # Make the accounting entries here
            make_acct_entries(user, self, amount)

            return True

        return False

    def void_payment(self, user, amount):
        self.balance += amount
        self.payments_credits -= amount
        self.save()
        # only void approved and non-zero payments
        for payment in self.payment_set.filter(
                                status_detail='approved',
                                amount__gt=0):
            payment.status_detail = 'void'
            payment.save()

        # reverse accounting entries
        make_acct_entries_reversing(user, self, amount)

    def void(self, user=None):
        """
        Voids invoice. This means the debt is no longer owed.
        """
        if not self.is_void:
            self.is_void = True
            self.void_date = datetime.now()
            self.voided_by = user
            # set balance to 0
            self.balance = 0
            self.save()

            # reverse accounting entries
            if self.subtotal > 0:
                make_acct_entries_initial_reversing(user, self, self.subtotal)

    @property
    def calculated_cancellation_fees(self):
        """Sum of all cancellation fees"""
        data = self.invoicelineitem_set.filter(
            description=self.LineDescriptions.CANCELLATION_FEE
        ).aggregate(models.Sum('total'))

        return data.get('total__sum') or 0

    @property
    def cancellation_fee_count(self):
        """Count of all cancellation fees"""
        return self.invoicelineitem_set.filter(
                description=self.LineDescriptions.CANCELLATION_FEE).count()

    @property
    def total_cancellation_fees(self):
        """
        Use cancellation fees originally calculated at
        cancellation, or use adjusted amount.
        """
        fees = self.adjusted_cancellation_fees

        if fees is None:
            fees = self.calculated_cancellation_fees

        return 0 if fees > self.total_less_refunds else fees

    @property
    def pending_cancellation_fees(self):
        """Cancellation fees still pending"""
        if not self.total_cancellation_fees:
            return 0

        return self.total_cancellation_fees - self.applied_cancellation_fees

    @property
    def default_cancellation_fees(self):
        """
        Default cancellation fees will either be
        the total cancellation fees on the invoice or the default
        for the registration.
        """
        if not self.registration:
            return 0

        fees = self.total_cancellation_fees or self.registration.default_cancellation_fees

        return 0 if fees > self.total_less_refunds else fees

    @property
    def can_refund(self):
        """
        Indicate if invoice can be refunded.
        Invoice can be refunded if refunds are allowed in
        site settings, there is a refundable amount, and
        the refundable amount has been paid through Stripe (has trans_id).
        """
        allow_refunds = get_setting('module', 'events', 'allow_refunds')

        return (
            allow_refunds != "No" and
            self.refundable_amount > 0 and
            self.refundable_amount_paid
        )

    @property
    def can_auto_refund(self):
        """
        Indicates auto refunds are allowed.
        Setting must be enabled, and refundable amount
        """
        allow_refunds = get_setting('module', 'events', 'allow_refunds')

        return allow_refunds == "Auto" and self.can_refund

    @property
    def refund_disabled_reason(self):
        if get_setting('module', 'events', 'allow_refunds') == "No":
            return "Refunds can be enabled by an administrator."

        if not self.refundable_amount:
            return "No refundable amount."

        if not self.refundable_amount_paid:
            return "Refundable amount must be paid."

    @property
    def total_less_refunds(self):
        """Invoice total minus refunds"""
        return self.total - self.refunds

    @property
    def refundable_amount(self):
        """Invoice total minus cancellation fees and refunds"""
        return max(self.total_less_refunds - self.total_cancellation_fees, 0)

    def get_refund_amount(self, amount):
        """
        Get refund amount and adjust for cancellation fees if applicable.
        """
        if amount < self.refundable_amount and amount > self.pending_cancellation_fees:
            return amount - self.pending_cancellation_fees

        # Full refundable amount is already adjusted for cancellation fees
        return min(amount, self.refundable_amount)

    @property
    def refundable_amount_paid(self):
        """Indicate whether refundable amount has been paid"""
        return self.total_paid >= self.refundable_amount

    @property
    def net_refunds(self):
        """Returns net amount of refunds"""
        return self.refunds * -1

    def refund(self, amount, user=None, confirmation_message=None, notes=None):
        """
        Refund specified amount. Cancellation fees are not refundable and will be
        deducted from refund. Max refund is the total invoice.
        Only allowed if allow_refunds site setting is on.
        """
        if amount <= 0:
            raise ValidationError(_("Amount refunded must be greater than 0."))

        if not self.can_refund:
            raise ValidationError(_(f"Refunds not allowed. {self.refund_disabled_reason}"))

        if amount > self.refundable_amount:
            raise ValidationError(
                _(f"Can only refund a maximum of ${self.refundable_amount}")
            )

        # Create confirmation message prior to refund so we have the
        # correct amount of pending cancellation fees.
        confirmation_message = confirmation_message or self.get_refund_confirmation_message(amount)

        # Execute refund. Alert admin if it fails.
        try:
            self.__refund(user, amount, notes=notes)
        except Exception as e:
            self.__send_failed_refund_notice(amount, e)
            raise

        # Update line item to show refund
        self.add_line_item(
            amount=-amount,
            description=self.LineDescriptions.REFUND,
            user=user,
            update_total=False
        )

        # Send email to confirm refund.
        if self.owner and self.owner.email:
            email = self.owner.email
        else:
            email = self.bill_to_email
        if email:
            self.__send_refund_confirmation(amount, confirmation_message, [email])

    def __refund(self, user, refund_amount, notes=None):
        """
        Updates the invoice balance by adding
        accounting entries for refunds and initiates actual refund.
        """
        amount = min(refund_amount, self.total_paid)
        if self.is_tendered and amount:
            self.__execute_refund_transaction(amount, notes=notes)
            self.refunds += amount
            self.save()

            make_acct_entries_refund(user, self, amount)

            # Apply any relevant cancellation fees
            if self.pending_cancellation_fees > 0:
                self.applied_cancellation_fees += self.pending_cancellation_fees
                self.save(update_fields=['applied_cancellation_fees'])

    def __execute_refund_transaction(self, amount, notes=None):
        """Execute refund for amount given it's covered by refundable payments"""
        payments = self.payment_set.refundable()

        remaining_amount = amount

        for payment in payments:
            refundable_amount = min(remaining_amount, payment.refundable_amount)
            available_amount = payment.refundable_amount
            if refundable_amount:
                # If there's an error, it will be raised and an email will be sent to admin.
                payment.refund(refundable_amount, notes=notes)

            if remaining_amount <= available_amount:
                break

            remaining_amount -= available_amount

    def __send_failed_refund_notice(self, amount, error):
        """Send Admin notice in case of failed refund"""
        recipients = get_notice_recipients('site', 'global', 'allnoticerecipients')
        if recipients:
            message = self.get_refund_failure_message(amount, error)
            self.__send_refund_confirmation(
                amount, message, recipients, is_admin_notice=True, failed=True)

    def __send_refund_confirmation(
            self,
            amount,
            confirmation_message,
            recipients,
            is_admin_notice=False,
            failed=False,
        ):
        """Send refund confirmation email"""
        invoice_url = None

        if not confirmation_message:
            confirmation_message = self.get_refund_confirmation_message(amount)
            invoice_url = reverse('invoice.view', args=[self.pk, self.guid]),

        notification.send_emails(recipients, 'refund_confirmation', {
            'confirmation_message': confirmation_message,
            'SITE_GLOBAL_SITEURL': get_setting('site', 'global', 'siteurl'),
            'SITE_GLOBAL_SITEDISPLAYNAME': get_setting('site', 'global', 'sitedisplayname'),
            'invoice': self,
            'is_admin_notice': is_admin_notice,
            'title': self.split_title(),
            'failed': failed,
        })

    @property
    def event(self):
        """Return Event tied to invoice (if there is one)"""
        obj = self.get_object()
        return getattr(obj, 'event', None)

    @property
    def registration(self):
        """If Invoice is tied to an event, then the obj is a Registration"""
        if self.event:
            obj = self.get_object()
            return obj
        return None

    @property
    def registered_count(self):
        """Count currently registered"""
        if not self.registration:
            return 0

        return self.registration.registrant_set.filter(cancel_dt__isnull=True).count()
    
    def object_display(self, obj=None):
        if not obj:
            obj = self.get_object()
        class_name = obj.__class__.__name__
        if class_name == 'Registration':
            return obj.event.title
        elif class_name == 'MembershipDefault':
            return obj.membership_type.name
        elif class_name == 'MembershipSet':
            return obj.membership_type
        return obj

    def get_payment_description(self, obj=None):
        desc = f'Invoice {self.id}'
        if not obj:
            obj = self.get_object()
        if obj:
            desc = obj.get_payment_description(self)
            if not desc:
                desc = f'Invoice {self.id} ({obj})'
        return desc

    def obj_donation(self):
        obj = self.get_object()
        return hasattr(obj, 'donation') and obj.donation

    def cancel_registration(self, request, refund=False):
        """Cancel registration for this invoice"""
        if not self.registration:
            raise Exception(_("No registration to cancel."))

        self.registration.cancel(request, refund)

    def get_refund_failure_message(self, amount, error):
        """Get default refund failure message"""
        message = f"Refund to {self.owner.first_name} {self.owner.last_name} in amount ${amount} " \
                  f"failed to process through Stripe"

        if self.event:
            message += f" for {self.event.title} on {self.event.display_start_date}"

        return f"{message}. Reason for failure: {error}."

    def get_refund_confirmation_message(self, amount):
        """Get default refund confirmation message"""
        cancellation_fee_message = ""

        # If no refundable amount remains after refund, then cancellation fees
        # have been processed.
        if self.pending_cancellation_fees and amount > self.pending_cancellation_fees:
            cancellation_fee_message = f" and a cancellation fee of " \
                                       f"${self.pending_cancellation_fees} has been processed"

        message = f"You have been refunded ${amount}"

        if self.event:
            message = f"Your registration fee in the amount of ${amount} for " \
                      f"{self.event.title} on {self.event.display_start_date} has been refunded"

        return f"{message}{cancellation_fee_message}."

    @property
    def admin_refund_confirmation_message(self):
        """Message to display to confirm refund completed"""
        if self.owner:
            profile_url = reverse('profile', args=[self.owner.username])
            name = f"{self.owner.first_name} {self.owner.last_name}"
            message = f"Refund to <a class='alert-link' href={profile_url}>{name}</a>"
        else:
            name = f"{self.bill_to} {self.bill_to_email}"
            message = f"Refund to {name}"

        if not self.event:
            return f"{message} has been processed."

        return f"{message} for {self.event.title} on {self.event.display_start_date} " \
               f"has been processed."

    @property
    def admin_refund_failure_message(self):
        """Message to display to confirm refund failed"""
        if self.owner:
            profile_url = reverse('profile', args=[self.owner.username])
            name = f"{self.owner.first_name} {self.owner.last_name}"
            message = f"Refund to <a class='alert-link' href={profile_url}>{name}</a>"
        else:
            name = f"{self.bill_to} {self.bill_to_email}"
            message = f"Refund to {name}"

        if not self.event:
            return f"{message} has failed to process through Stripe."

        return f"{message} for {self.event.title} on {self.event.display_start_date} " \
               f"has failed to process through Stripe."

    def update_cancellation_fee_line_item(self, new_amount, user=None):
        """Update cancellation fee line item"""
        self.invoicelineitem_set.filter(
            description=self.LineDescriptions.CANCELLATION_FEE,
        ).delete()

        self.add_line_item(new_amount, self.LineDescriptions.CANCELLATION_FEE, user, False)

    def add_line_item(self, amount, description, user=None, update_total=True):
        """
        Add extra line item to this invoice.
        Set update_total to False to exclude from invoice total.
        """
        InvoiceLineItem.objects.create(
            total=amount,
            description=description,
            invoice=self,
        )

        if update_total:
            self.total += amount
            self.subtotal += amount
            self.balance += amount
            self.save(user)

#     def unvoid(self):
#         """
#         Remove 'void' from invoice. This means the invoice is active again.
#         """
#         if self.is_void:
#             self.is_void = False
#             self.save()

    @property
    def total_paid(self):
        """
        Total of approved payments through Stripe,
        with a remaining refundable amount.
        """
        data = self.payment_set.refundable().aggregate(models.Sum('amount'))

        return data.get('amount__sum') or 0

    def get_first_approved_payment(self):
        """
        Returns first approved payment in ascending order
        """
        [payment] = self.payment_set.filter(status_detail='approved')[:1] or [None]
        return payment

    def stripe_connected_account(self, scope=''):
        """
        Get the stripe connected account for this invoice.
        """
        if not self.entity:
            return None, None

        if not get_setting('module', 'payments', 'stripe_connect_client_id'):
            return None, None
        
        stripe_accounts = StripeAccount.objects.filter(
                            entity=self.entity,
                            status_detail='active')

        if scope:
            stripe_accounts = stripe_accounts.filter(scope=scope)

        [stripe_account] = stripe_accounts[:1] or [None]
        if stripe_account:
            return stripe_account.stripe_user_id, stripe_account.scope 

        return None, None

    def get_stripe_application_fee(self, amount):
        return Decimal(amount) * Decimal(0.029) + Decimal(0.30)

    def get_invoice_logo_url(self):
        from tendenci.apps.files.models import File
        try:
            file_id = int(get_setting('module', 'invoices', 'invoicelogo'))
        except ValueError:
            file_id = 0
        if file_id:
            file = File.objects.filter(id=file_id).first()
            if file:
                return file.get_full_url()
        return ''


class InvoiceLineItem(models.Model):
    """
    Extra line items on an invoice.
    For example, a cancellation fee.
    """
    total = models.DecimalField(max_digits=15, decimal_places=2, blank=True)
    description = models.CharField(max_length=200, blank=True, null=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)


# add signals
post_save.connect(update_profiles_total_spend, sender=Invoice,
    dispatch_uid='tendenci.apps.invoices.models.update_profiles_total_spend')
