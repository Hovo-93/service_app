from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet

from clients.models import Client
from services.models import Subscription
from services.serializers import SubscriptionSerializer
from django.db.models import Prefetch, F, Sum


# Create your views here.


class SubscriptionView(ReadOnlyModelViewSet):
    # queryset = Subscription.objects.all().prefetch_related('client__user') retuened all all info user name email...
    # if we can get only email only the fields which we want
    queryset = Subscription.objects.all().prefetch_related(
        'plan',
        Prefetch('client', queryset=Client.objects.all().select_related('user').only('company_name', 'user__email')),
    ).annotate(price=F('service__full_price') - F('service__full_price') *
                     F('plan__discount_percent') / 100.00)
    # annotate(price) virtualnoe pole mer sarqace inchpes seralizeri-i meji price=
    # F_@ function e db.models-ic vori mijocov obrashaemsya k kakomu to polyu
    #
    serializer_class = SubscriptionSerializer

    def list(self, request, *args, **kwargs):
        # mer vervi zaprosne mer queryset@
        queryset = self.filter_queryset(self.get_queryset())
        response = super().list(request, *args, **kwargs)
        response_data ={'result':response.data}
        response.data = response_data
        # vortex price mer virtual sarqac polyane annotate F-i mijocov
        response_data['total_amount']=queryset.aggregate(total=Sum('price')).get('total')
        # total_amount dict e vercnum enq get-ov total-e
        # ": {
        # "total": 637.5
        # }

        # menq sa hashvum enq ogtagorcelov funkcian bazai makardakov

        print(response_data,'print response_data')
        return response
