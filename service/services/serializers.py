from rest_framework import serializers

from services.models import Subscription
from services.models import Plan

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ('__all__')

class SubscriptionSerializer(serializers.ModelSerializer):
    #vlojeni seralizer
    plan = PlanSerializer()

    # ete chenq uzem unenal id-n clienti ayl anune te vore uni podpiska (ete forntin petq che id-in dra hamar e spes grac)
    client_name = serializers.CharField(source='client.company_name')
    email = serializers.CharField(source='client.user.email')
    price = serializers.SerializerMethodField()
    # ete pole price menq piti anpayman grenq get_(variable) ete ogtagorcum enq serializers.SerializerMethodField()
    #Если Subscription модель имеет поле price,
    # и вы хотите использовать это поле в get_price, вы можете обратиться к нему так:
    def get_price(self,instance):
        print(instance)
        return instance.price #sa views i mer sarqac annotate price-n e
    #     # ays demqum unenum enq n+1 problem
    #     return (instance.service.full_price -
    #             instance.service.full_price*(instance.plan.discount_percent/100))
    #     """
    #          SELECT "services_service"."id", "services_service"."name", "services_service"."full_price"
    #          FROM "services_service" WHERE "services_service"."id" = 1 LIMIT 21; args=(1,)
    #          qani service unecanq etqan angam kkrknvi es zaprose n+! kdarna
    #
    #     """
        #bazai level-ov karox enq anel prefetch service bayc anum enq annotate-i ognutyamb
    class Meta:
        model = Subscription
        # plan_id chka Subscription modeli mej bayc qani vor ka Forein Key(one-to-many) Plan modeli hed uni id vortex soxranyaetysa idishnik etogo plana eto skritoe pole
        fields =('id','plan_id','client_name','email','plan','price')
