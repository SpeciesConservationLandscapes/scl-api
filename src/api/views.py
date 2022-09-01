from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ReportData
from .serializers import CountrySerializer




class CountryViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = CountrySerializer

    def get_queryset(self):
        model = self.serializer_class.Meta.model
        queryset = model.objects.exclude(iso2="AQ")

        iso2 = self.request.query_params.get("iso2")
        if iso2 is not None:
            queryset = queryset.filter(iso2=iso2)

        return queryset


class ChoicesView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        data = {
            "dates": [td["task_date"] for td in ReportData.objects.values("task_date").distinct().order_by("-task_date")]
        }
        print(f"data: {data}")
        return Response(data)
