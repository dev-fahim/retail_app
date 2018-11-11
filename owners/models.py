from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save

# Create your models here.


User = get_user_model()


class OwnerModel(models.Model):

    """
    Personal information
    """
    owner_name = models.OneToOneField(to=User, on_delete=models.CASCADE, related_name='owner')
    owner_birth_date = models.DateField(blank=True, null=True)
    owner_ps_address = models.TextField(blank=False, default='N/A')
    owner_pm_address = models.TextField(blank=False, default='N/A')

    """
    Owner's status
    """
    owner_joined = models.DateTimeField(auto_now_add=True)
    owner_info_updated = models.DateTimeField(auto_now=True)
    owner_is_active = models.BooleanField(default=False)
    owner_profile_submitted = models.BooleanField(default=False)
    owner_is_approved = models.BooleanField(default=False)
    owner_is_online = models.BooleanField(default=False)

    """
    Important methods
    """
    def __str__(self):
        return self.owner_name.username

    def is_active(self):
        return self.owner_is_active

    def is_approved(self):
        return self.owner_is_approved

    def is_online(self):
        return self.owner_is_online

    class Meta:
        verbose_name = 'Owner'


class OwnerStoreModel(models.Model):
    CHOICES_STORE_TYPE = (
        ('gn_store', 'General Store'),
        ('ph_store', 'Pharmacy Store'),
        ('ch_store', 'Chain Shop'),
        ('sp_store', 'Sports Shop')
    )

    """
    Owner of the store
    """
    owner_store = models.ForeignKey(to=OwnerModel, on_delete=models.CASCADE, related_name='store')

    """
    Owner's store information
    """
    owner_store_name = models.CharField(max_length=100, blank=False)
    owner_store_lcs_type = models.CharField(max_length=45, blank=False, default='N/A')
    owner_store_address = models.TextField(blank=False)
    owner_store_type = models.CharField(choices=CHOICES_STORE_TYPE, blank=False, default=CHOICES_STORE_TYPE[0][0],
                                        max_length=40)

    """
    Owner's store status
    """
    owner_store_added = models.DateTimeField(auto_now_add=True)
    owner_store_updated = models.DateTimeField(auto_now=True)
    owner_store_profile_submitted = models.BooleanField(default=False)
    owner_store_is_approved = models.BooleanField(default=False)
    owner_store_is_online = models.BooleanField(default=False)

    """
    Important methods
    """
    def __str__(self):
        return self.owner_store_name

    def is_approved(self):
        return self.owner_store_is_approved

    def is_online(self):
        return self.owner_store_is_online

    @property
    def get_owner_name(self):
        return str(self.owner_store.owner_name)

    class Meta:
        verbose_name = 'Store'


class StoreProductModel(models.Model):

    """
    Product information
    """
    product_store = models.ForeignKey(to=OwnerStoreModel, on_delete=models.CASCADE, related_name='products')
    store_product_owner = models.ForeignKey(OwnerModel, on_delete=models.CASCADE, related_name='owner_product', null=True)
    product_name = models.CharField(max_length=255)
    product_id = models.CharField(max_length=255, unique=True)

    """
    Product prices
    """
    product_price = models.IntegerField()
    product_main_price = models.IntegerField()

    def __str__(self):
        return self.product_name

    @property
    def get_store_name(self):
        return str(self.product_store.owner_store_name)


class ProductStatusModel(models.Model):

    """
    Product
    """
    product_origin = models.OneToOneField(StoreProductModel, on_delete=models.CASCADE, related_name='product')
    product_owner = models.ForeignKey(OwnerModel, on_delete=models.CASCADE, related_name='owner_product_status', null=True)

    """
    Product status
    """
    product_is_in_store = models.BooleanField(default=False)
    product_is_for_sale = models.BooleanField(default=False)
    product_quantity = models.IntegerField(default=0)

    """
    Important methods and properties
    """

    def is_is_store(self):
        return self.product_is_in_store

    def is_for_sale(self):
        return self.product_is_for_sale

    def qty_in_store(self):
        return self.product_quantity

    @property
    def get_name(self):
        return str(self.product_origin.product_name)

    @property
    def get_store(self):
        return str(self.product_origin.product_store)

    @property
    def get_price(self):
        return str(self.product_origin.product_price)

    @property
    def get_main_price(self):
        return str(self.product_origin.product_main_price)

    @property
    def get_pid(self):
        return str(self.product_origin.product_id)

    def __str__(self):
        return self.product_origin.product_name


"""All signals"""


def user_register_post_save_owner(sender, instance, created, *args, **kwargs):
    if created:
        OwnerModel.objects.create(owner_name=instance)


def store_product_on_add_post_save_product(sender, instance, created, *args, **kwargs):
    if created:
        ProductStatusModel.objects.create(product_origin=instance)


post_save.connect(user_register_post_save_owner, sender=User)
post_save.connect(store_product_on_add_post_save_product, sender=StoreProductModel)


"""-------------------"""