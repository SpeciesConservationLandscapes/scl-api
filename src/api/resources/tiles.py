import requests
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
from rest_framework.exceptions import NotFound, APIException, ValidationError


import ee

ee.Initialize()
img = ee.Image("projects/SCL/v1/Panthera_tigris/source/Inputs_2006/density")
vis_params = {
    format: 'png'
}

map_id = img.getMapId(vis_params)
print(map_id)


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
    x = int(x)
    y = int(y)
    z = int(z)

    tile_url = ee.data.getTileUrl(map_id, x, y, z)
    resp = requests.get(tile_url)
    status_code = resp.status_code
    if status_code == 404:
        raise NotFound()
    if status_code >= 500:
        raise APIException()
    return Response(
        data=resp.content, content_type="image/png", headers={"content-type": "image/png"}
    )
