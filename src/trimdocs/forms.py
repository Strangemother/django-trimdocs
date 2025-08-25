from django import forms
from trim.forms import fields


class CompileConfirmForm(forms.Form):
    do_compile = fields.boolean(required=False)