import logging

from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from app.bot_ai.api.serializers import CompanyDataSerializer
from app.bot_ai.api.serializers import ProductDataSerializer
from app.bot_ai.models import CompanyData
from app.bot_ai.models import ProductData

logger = logging.getLogger(__name__)


class CompanyDataView(APIView):
    permission_classes = [AllowAny]
    serializer_class = None

    def get(self, request, *args, **kwargs):
        logger.debug("CompanyDataView.get()-------------------------")
        companies = CompanyData.objects.all()
        serializer = CompanyDataSerializer(companies, many=True)
        return Response(serializer.data)


class ProductDataListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = ProductData.objects.all()
    serializer_class = ProductDataSerializer
