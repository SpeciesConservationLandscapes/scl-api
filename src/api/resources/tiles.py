from django.core.files import File
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
    renderer_classes,
)
from rest_framework.renderers import BaseRenderer
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import ee


def _initialize_ee_client(self):
    if self.service_account_key is None:
        ee.Initialize("persistent")
    else:
        service_account_name = json.loads(self.service_account_key)["client_email"]
        credentials = ee.ServiceAccountCredentials(
            service_account_name, key_data=self.service_account_key
        )
        ee.Initialize(credentials)


class PngRenderer(BaseRenderer):
    media_type = "image/png"
    format = "png"
    charset = None
    render_style = "binary"

    def render(self, data, media_type=None, renderer_context=None):
        return data


# class PAView(APIView):
#     renderer_classes = [PngRenderer]
#     # authentication_classes = [authentication.TokenAuthentication]
#     # permission_classes = [permissions.IsAdminUser]
#
#     def get(self, request, format=None):
#         img = "/var/projects/webapp/Capture.PNG"
#         return Response(data=img)


@api_view(["GET", "HEAD", "OPTIONS"])
@authentication_classes([])
@permission_classes((AllowAny,))
@renderer_classes((PngRenderer,))
def pas(request, z, x, y):
    print(z, x, y)
    img = File(open("/var/projects/webapp/Capture.PNG", "rb"))
    return Response(
        data=img, content_type="image/png", headers={"content-type": "image/png"}
    )
