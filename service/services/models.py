from django.core.validators import MaxValueValidator
from django.db import models

from services.singals import delete_cache_total_sum
from services.tasks import set_price
from clients.models import Client

from django.db.models.signals import post_delete
# Create your models here.


class Service(models.Model):
    name = models.CharField(max_length=50)
    full_price = models.PositiveIntegerField()
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.__full_price = self.full_price

    def save(self,*args,**kwargs ):
        if self.full_price != self.__full_price:
            for subscription in self.subscriptions.all():
                set_price.delay(subscription.id)
        return super().save(*args,**kwargs)


class Plan(models.Model):
    PLAN_TYPES = (
        ('full', 'Full'),
        ('student', 'Student'),
        ('discount', 'Discount')

    )
    plan_type = models.CharField(choices=PLAN_TYPES, max_length=10)
    discount_percent = models.PositiveIntegerField(default=0,
                                                   validators=[
                                                       MaxValueValidator(100)
                                                   ])

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.__discount_percent = self.discount_percent



    def save(self, *args,**kwargs):
        if self.discount_percent != self.__discount_percent:
            # тогда и запускаем пересчет для подписок
            for subscription in self.subscriptions.all():
                set_price.delay(subscription.id)

        return super().save(*args,**kwargs)

class Subscription(models.Model):
    # related_name eto to s kakim imenem ona budet dostupna vnutri v Client- clinet.sunscipsion.all podpiski clients
    # subscritions.filter(client=client_id).all oba odinakovie
    # esli chere klienta xoptim uvidet podpiski to ispolzuem subscriptions(related_name)
    client = models.ForeignKey(Client, related_name='subscriptions', on_delete=models.PROTECT)
    # u servisa budut podpiski service.subscritions.all
    service = models.ForeignKey(Service, related_name='subscriptions', on_delete=models.PROTECT)

    plan = models.ForeignKey(Plan, related_name='subscriptions', on_delete=models.PROTECT)
    price = models.PositiveIntegerField(default=0,db_index=True)
    # Subscription.objects.filter(plan='100').explain(analyze=True) proverim ka delat filter baza dannix
    field_a = models.CharField(max_length=40)
    field_b = models.CharField(max_length=40)
    #sxal reshenia
    # def save(self, *args,save_model=True,**kwargs,):
    #    if save_model:
    #        set_price.delay(self.id) #cross import
    #
    #    return super().save( *args,**kwargs)
    #sxal e qani vor menq petq e  anenq пересчет в момент сохранения subscrition а в момент сохранения других моделей
    #orinak service.full_price,discount_percent popoxvel e miayn ayd jamanak pereshet petqe anel
    def save(self, *args, **kwargs):
        # kak ponyat kogda sozdaetsya subrsriptiopn
        creating =  not bool(self.id)
        result = super().save(*args, **kwargs)
        if creating: #esli sozdalos
            set_price.delay(self.id)
        return result

    class Meta:
        # Составной индекс если хотим по несколким индексированим полям делать фиотр
        indexes = [
            models.Index(fields=['field_a','field_b'])

        ]


post_delete.connect(delete_cache_total_sum,sender=Subscription)