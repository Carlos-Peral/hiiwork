from django import forms
from apps.gigs.models import Gig, Package, Feature, Extra, FAQ, Requirement, RequirementClient


class GigForm(forms.ModelForm):
    """Form definition for Gig."""

    class Meta:
        """Meta definition for Gigform."""
        model = Gig
        fields = ['title', 'description', 'category']


class PackageForm(forms.ModelForm):
    """Form definition for Package."""

    class Meta:
        """Meta definition for Packageform."""
        model = Package
        fields = ['description', 'deliveryTime', 'revisions', 'price']


class FAQsForm(forms.ModelForm):
    """Form definition for FAQs."""

    class Meta:
        """Meta definition for FAQsform."""
        model = FAQ
        fields = ['question', 'answer']


class FeatureForm(forms.ModelForm):
    """Form definition for Feature."""
    class Meta:
        """Meta definition for Featureform."""
        model = Feature
        fields = ['name', 'tier1', 'tier2', 'tier3']


class ExtraForm(forms.ModelForm):
    """Form definition for Extra."""

    class Meta:
        """Meta definition for ExtraForm."""
        model = Extra
        fields = ['title', 'description', 'price1',  'extraDays1', 'numberOfTimesYouCanBuy1',
                  'price2', 'extraDays2', 'numberOfTimesYouCanBuy2', 'price3', 'extraDays3', 'numberOfTimesYouCanBuy3']


class FastExtraForm(forms.ModelForm):
    """Form definition for FastExtra."""

    class Meta:
        """Meta definition for ExtraForm."""
        model = Extra
        fields = ['price1', 'extraDays1', 'price2',
                  'extraDays2', 'price3', 'extraDays3']


class RequirementForm(forms.ModelForm):
    """Form definition for Requirement."""

    class Meta:
        """Meta definition for RequirementForm."""
        model = Requirement
        fields = ['requirement', 'description']


class FastExtraOrder(forms.Form):
    """FastExtraOrder definition."""
    extra_B = forms.BooleanField(required=False)
    extra_N = forms.BooleanField(required=False)
    extra_P = forms.BooleanField(required=False)
    extra = None

    def __init__(self, *args, **kwargs):
        self.extra = kwargs.pop('extra')
        super(FastExtraOrder, self).__init__(*args, **kwargs)


class ExtraOrder(forms.Form):
    """FastExtraOrder definition."""
    extra = None

    def __init__(self, *args, **kwargs):
        self.extra = kwargs.pop('extra')
        super(ExtraOrder, self).__init__(*args, **kwargs)

        self.fields['extra_B'] = forms.ChoiceField(
            choices=[(i, '%s' % i) for i in range(self.extra.numberOfTimesYouCanBuy1 + 1)], label="Cant.")
        self.fields['extra_N'] = forms.ChoiceField(
            choices=[(i, '%s' % i) for i in range(self.extra.numberOfTimesYouCanBuy2 + 1)], label="Cant.")
        self.fields['extra_P'] = forms.ChoiceField(
            choices=[(i, '%s' % i) for i in range(self.extra.numberOfTimesYouCanBuy3 + 1)], label="Cant.")


class CheckOutExtra(forms.Form):
    """CheckOutExtra definition."""
    extra = None
    is_selected = forms.BooleanField(required=False)
    quantity = None

    def __init__(self, *args, **kwargs):
        self.extra = kwargs.pop('extra')
        self.quantity = kwargs.pop('quantity')
        super(ExtraOrder, self).__init__(*args, **kwargs)


class RequirementClientForm(forms.ModelForm):
    """Form definition for FastExtra."""

    class Meta:
        """Meta definition for ExtraForm."""
        model = RequirementClient
        fields = ['comments']
