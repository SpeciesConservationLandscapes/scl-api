import json
import os

from osgeo import ogr


mask_wkt = (
    "POLYGON((-180.0 -85.06,-180.0 85.06,180.0 85.06,180.0 -85.06,-180.0 -85.06))"
)


def split_by_feature(
    file_path,
    output_dir,
    name_field,
    include_properties=False,
    layer=None,
    mask_diff=False,
):
    ds = ogr.Open(file_path)
    lyr = ds.GetLayer(layer) if layer else ds.GetLayer()
    ft = lyr.GetNextFeature()
    while ft:
        if mask_diff:
            mask = ogr.CreateGeometryFromWkt(mask_wkt)
            geom = ft.GetGeometryRef()
            clipped_mask = mask.Difference(geom)
            ft.SetGeometry(clipped_mask)

        name = ft.GetFieldAsString(name_field)
        geojson = ft.ExportToJson()
        if include_properties is False:
            geojson = json.loads(geojson)
            geojson["properties"] = {}
            geojson = json.dumps(geojson)

        with open(f"{os.path.join(output_dir, name)}.geojson", "w") as w:
            w.write(geojson)

        ft = lyr.GetNextFeature()


if __name__ == "__main__":
    split_by_feature(
        "data/GDAM404_country_simp2.shp", "output2", "iso2", mask_diff=True
    )
