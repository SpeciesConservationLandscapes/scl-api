from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import CharField, Max
from django.forms import TextInput
from django.forms.models import BaseInlineFormSet
from django.utils.html import format_html
from api.admin import BaseAdmin


def zotero_link(obj, show_code=True):
    display_text = obj
    if hasattr(obj, "reference"):
        display_text = obj.reference
    if show_code:
        display_text = obj.zotero
    return format_html(
        f'<a href="https://www.zotero.org/groups/{settings.ZOTERO_GROUP}/items/itemKey/{obj.zotero}" target="_blank">'
        f"{display_text}</a>"
    )


zotero_link.admin_order_field = "zotero"


class CanonicalInlineFormset(BaseInlineFormSet):
    atleast_one = False

    def clean(self):
        super().clean()
        if any(self.errors):
            return
        modelname = self.queryset.model._meta.verbose_name
        parentname = self.instance._meta.verbose_name

        # If only one inline form, mark it canonical on user's behalf
        if len(self.forms) == 1:
            self.forms[0].cleaned_data["canonical"] = True

        if self.atleast_one:
            if not any(
                cleaned_data and not cleaned_data.get("DELETE", False)
                for cleaned_data in self.cleaned_data
            ):
                raise ValidationError(f"At least one {modelname} is required")

        canonical_instances = []
        for form in self.forms:
            data = form.cleaned_data

            if data.get("canonical", False) and not data["DELETE"]:
                canonical_instances.append(form.instance.__str__())

        # Not more than one canonical instance must be marked...
        if len(canonical_instances) > 1:
            raise ValidationError(
                f"Only one {modelname} for this {parentname} may be marked canonical. "
                f"Deselect one of: {'; '.join(canonical_instances)}"
            )

        # ...and at least one must be marked
        if len(self.forms) and self.atleast_one:
            if len(canonical_instances) < 1:
                raise ValidationError(
                    f"One {modelname} for this {parentname} must be marked canonical."
                )


class BaseObservationAdmin(BaseAdmin):
    readonly_fields = ["created_by", "created_on", "updated_by", "updated_on"]
    formfield_overrides = {CharField: {"widget": TextInput(attrs={"size": "100%"})}}

    def save_model(self, request, obj, form, change):
        profile = request.user.obsprofile
        if change:
            obj.created_by = profile
        obj.updated_by = profile
        super().save_model(request, obj, form, change)


class TypeAdmin(BaseObservationAdmin):
    list_display = ["sequence", "name", "description", "examples"]
    list_display_links = ["sequence", "name"]
    fields = [
        "sequence",
        "name",
        "description",
        "examples",
        ("created_by", "created_on"),
        ("updated_by", "updated_on"),
    ]

    def get_changeform_initial_data(self, request):
        max_sequence = (
            self.model.objects.aggregate(Max("sequence"))["sequence__max"] or 0
        )
        return {"sequence": max_sequence + 1}
