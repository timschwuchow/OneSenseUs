from django import forms
from models import Facet, General, Project


class FacetSelectionForm(forms.Form):
    facets = forms.ModelMultipleChoiceField(queryset=Facet.objects.all(), widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        gid = kwargs.pop('gid', None)
        super(FacetSelectionForm, self).__init__(*args, **kwargs)
        if gid:
            qs = Facet.objects.filter(general=General.objects.get(pk=int(gid)))
            self.fields['facets'].queryset = qs


class GeneralSelectionForm(forms.Form):
    '''
    Select bundles of generals to implement finished project
    '''
    generals = forms.ModelMultipleChoiceField(queryset=General.objects.all(),widget=forms.CheckboxSelectMultiple)
    def __init__(self, *args, **kwargs):
        pid = kwargs.pop('pid', None)
        super(GeneralSelectionForm, self).__init__(*args, **kwargs)
        try:
            p = Project.objects.get(pk=int(pid))
        except:
            pass
        else:
            qs = General.objects.filter(project=p)
            self.fields['generals'].queryset = qs
