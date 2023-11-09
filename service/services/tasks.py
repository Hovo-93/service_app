import time

from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.db.models import F

from celery import shared_task
from celery_singleton import Singleton


# cross import
# from services.models import Subscription
@shared_task(base=Singleton)
def set_price(subscription_id):
    time.sleep(7)
    from services.models import Subscription
    # vercnum enq id-in voch che henc (obyekt subscriptione) vorovhetev minchev na gtnvume herti mej karox e ay objecte poxvel
    # u nor popoxutyunere menq chenq stana ete chvercnenq id-n
    # to est vitaskivat iz bazi tolko kogda taska zapustitya a do etogo prosto xranit ego idshnik
    # subscription=Subscription.objects.get(id=subscription_id)
    # new_price = subscription.service.full_price - \
    #             subscription.service.full_price * subscription.plan.discount_percent/100
    # subscription.price = new_price
    # optimization

    with transaction.atomic():# libo fse libo nichego atmorano to est
        subscription = Subscription.objects.filter(id=subscription_id).annotate(annotate_price=F('service__full_price') -
                                                                                               F('service__full_price') *
                                                                                               F('plan__discount_percent') / 100.00).first()
        subscription.price = subscription.annotate_price
        print(subscription.price,'==============================')
        # subscription.save(save_model=False)
        subscription.save()
    # invalidiruem cache to esti naxqan sa avelacnele ete menq price kam discount einq poxov minchev 30sec chancner cashe cher poxvi
    # dra hamar invalidiruem aysinqn jnjum enq anmijapes heto erp vor price poxvav vor cuyc tanq 30 sec chspasenq
    cache.delete(settings.PRICE_CACHE_NAME)
