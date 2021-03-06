from rest_framework import serializers
from sales.models import SalesModel, DailySalesModel
from owners.stores.models import OwnerStoreModel
from rest_framework import exceptions
from owners.products.models import StoreProductModel


class DailySalesSerializer(serializers.ModelSerializer):

    product_name = serializers.SerializerMethodField(read_only=True)
    id = serializers.IntegerField(required=False)
    elect = serializers.BooleanField(default=True)

    class Meta:
        model = DailySalesModel
        fields = ('id', 'sales', 'product_name', 'product', 'discounted', 'elect')
        read_only_fields = ('sales', )

    @staticmethod
    def get_product_name(obj):
        return obj.get_product_name

    def validate_product(self, value):
        if value.object_owner != self.get_logged_in_user().owner:
            raise serializers.ValidationError('Product not found', 404)
        return value

    def get_logged_in_user(self, obj):
        request = self.context['request']
        user = str(request.user.owner)

        return user


class SalesSerializer(serializers.ModelSerializer):

    sales_object = DailySalesSerializer(read_only=False, many=True)
    sale_id = serializers.UUIDField()
    owner_name = serializers.SerializerMethodField(read_only=True)
    store_name = serializers.SerializerMethodField(read_only=True)
    urls = serializers.HyperlinkedIdentityField(
        view_name='api_sales:sales_detail_api_view',
        lookup_field='id',
        read_only=True
    )
    logged_in_user = serializers.SerializerMethodField(read_only=True)
    user_level = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SalesModel
        fields = ('logged_in_user', 'id', 'urls', 'owner_name', 'object_owner',
                  'store', 'store_name', 'sale_id', 'total_discounted', 'sales_object')
        read_only_fields = ('object_owner', 'sale_id')

    def get_logged_in_user(self, obj):
        user = str(self.current_user().owner)

        return user

    def current_user(self):
        return self.request_data().user

    def request_data(self):
        return self.context['request']

    def get_user_level(self, obj):
        user_level = self.current_user().user_level.all()
        return user_level.level

    def validate_store(self, value):
        if OwnerStoreModel.objects.filter(object_owner=self.current_user().owner, id=value.id).exists() is False:
            raise serializers.ValidationError('Store not found', 404)
        return value

    def create(self, validated_data):
        request = self.context['request']
        if OwnerStoreModel.objects.filter(object_owner=request.user.owner, id=validated_data.get('store').id).exists():
            if validated_data.get('sales_object'):
                products_data = validated_data.pop('sales_object')
                sales = SalesModel.objects.create(object_owner=request.user.owner, **validated_data)
                for product_data in products_data:
                    if product_data.get('product').object_owner == request.user.owner:
                        product_data.pop('elect')
                        pid = product_data.pop('id')
                        if StoreProductModel.objects.filter(
                                product_store=validated_data.get('store'),
                                object_owner=request.user.owner,
                                product_id=pid).exists():
                            DailySalesModel.objects.create(sales=sales, **product_data)
                        else:
                            raise exceptions.ValidationError('Store and product not found', 404)
                    else:
                        raise exceptions.ValidationError('Product not found', 404)
                return sales
            else:
                validated_data.pop('sales_object')
                sales = SalesModel.objects.create(object_owner=request.user.owner, **validated_data)
                return sales
        else:
            raise exceptions.ValidationError('Store not found', 404)

    def update(self, instance, validated_data):
        request = self.context['request']
        if SalesModel.objects.filter(object_owner=request.user.owner, store=validated_data.get('store')).exists():
            products_validated_data = validated_data.pop('sales_object')

            instance.object_owner = validated_data.get('object_owner', instance.object_owner)
            instance.store = validated_data.get('store', instance.store)
            instance.sale_id = validated_data.get('sale_id', instance.sale_id)
            instance.total_discounted = validated_data.get('total_discounted', instance.total_discounted)
            instance.save()

            activated_ids = []
            for product in products_validated_data:
                if product.get('product').object_owner == request.user.owner:
                    if 'id' in product.keys() and product.get('elect') is True:
                        if product.get('id') is not 0:
                            if DailySalesModel.objects.filter(id=product.get('id'), sales=instance).exists():
                                if StoreProductModel.objects.filter(
                                        product_store=validated_data.get('store'),
                                        object_owner=request.user.owner,
                                        product_id=product.get('id')).exists():
                                    sale = DailySalesModel.objects.get(id=product.get('id'), sales=instance)
                                    sale.product = product.get('product', sale.product)
                                    sale.discounted = product.get('discounted', sale.discounted)
                                    activated_ids.append(sale.id)
                                    print(product)
                                    sale.save()
                                else:
                                    raise exceptions.ValidationError('1. Store and product not found', 404)
                            else:
                                continue
                        elif product.get('id') == 0:
                            if StoreProductModel.objects.filter(
                                    product_store=validated_data.get('store'),
                                    object_owner=request.user.owner,
                                    product_id=product.get('id')).exists():
                                new_sale = DailySalesModel.objects.create(
                                    product=product.get('product'),
                                    sales=instance,
                                    discounted=product.get('discounted')
                                )
                                activated_ids.append(new_sale.id)
                            else:
                                raise exceptions.ValidationError('2. Store and product not found', 404)
                    elif DailySalesModel.objects.filter(id=product.get('id'), sales=instance).exists() \
                            and product.get('elect') is False:
                        del_sale = DailySalesModel.objects.get(id=product.get('id'), sales=instance)
                        del_sale.delete()
                    else:
                        continue
                else:
                    raise exceptions.ValidationError('Product not found', 404)
            return instance
        else:
            raise exceptions.ValidationError('Store not found', 404)

    @staticmethod
    def get_owner_name(obj):
        return obj.get_owner_name

    @staticmethod
    def get_store_name(obj):
        return obj.get_store_name
