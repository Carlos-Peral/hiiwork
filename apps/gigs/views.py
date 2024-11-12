from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelformset_factory
from django.views import View
from apps.gigs.forms import *
from apps.gigs.models import Gig, Package, Extra, Feature, FAQ, Order
from apps.profiles.models import UserProfile
from django.http import Http404
from apps.gigs.utils import OrderDecoder, PackageCalculator, ListFeatures, SomethingWrongException
from apps.orders.OrderManager import OrderManager
from django.conf import settings


class CreateGigBasicInfoView(View):

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        # Check if the user has an unfinished gig.
        try:
            # If he does, populate the form with the unfinished gig.
            unfinishedGig = Gig.objects.filter(
                author=request.user).get(isFinished=False)
            form = GigForm(instance=unfinishedGig)
            files = list(unfinishedGig.files.all())
            context = {'form': form, 'files': files}
        except:
            # If he doesn't, just crete a blank form
            gig = Gig()
            gig.author = request.user
            gig.save()
            form = GigForm(instance=gig)
            context = {'form': form}

        return render(request, 'gigs/create.html', context=context)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        form = GigForm(request.POST)
        if form.is_valid():
            try:
                unfinishedGig = Gig.objects.filter(
                    author=request.user).get(isFinished=False)
                gig_form = GigForm(request.POST, instance=unfinishedGig)
                gig_form.save()
            except:
                gig = form.save(commit=False)
                gig.author = request.user
                gig.save()
            return redirect('packages/')


class CreateGigPriceAndPackagesView(View):

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        # Check if the user has an unfinished gig.
        try:
            # If he does, get the Packages, Features and Extras asociated with it.
            unfinishedGig = Gig.objects.filter(
                author=request.user).get(isFinished=False)

            # Create the formset for each attribute
            packageFormsetFactory = modelformset_factory(
                Package, form=PackageForm, extra=3, max_num=3, min_num=3, validate_min=3)
            featuresFormsetFactory = modelformset_factory(
                Feature, form=FeatureForm, extra=10, max_num=10, min_num=0, validate_min=0)

            # Load the formsets with the existing packages and features (if any)
            packageFormset = packageFormsetFactory(
                queryset=Package.objects.filter(gig=unfinishedGig), prefix='package')
            featuresFormset = featuresFormsetFactory(
                queryset=Feature.objects.filter(gig=unfinishedGig), prefix='feature')
            context = {'packageFormset': packageFormset,
                       'featuresFormset': featuresFormset}
            return render(request, 'gigs/createPriceAndPackages.html', context=context)

        except Exception as e:
            print(e)
            # If therre is no unfinished gig, go to the create gig page.
            return redirect('/gigs/create')

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        try:
            # First we check if there is an unfinished gig
            unfinishedGig = Gig.objects.filter(
                author=request.user).get(isFinished=False)
            # Load the formsets
            packageFormsetFactory = modelformset_factory(
                Package, form=PackageForm, extra=3, max_num=3, min_num=3, validate_min=3)
            featuresFormsetFactory = modelformset_factory(
                Feature, form=FeatureForm, extra=10, max_num=10, min_num=0, validate_min=0)
            # Populate them with the request
            packageFormset = packageFormsetFactory(
                request.POST, request.FILES, prefix='package')
            featuresFormset = featuresFormsetFactory(
                request.POST, request.FILES, prefix='feature')
            # Check if they are valid
            if packageFormset.is_valid() and featuresFormset.is_valid():
                # Delete all previous Packages and Features (it's safe now that everything is valid)
                savedPackages = Package.objects.filter(gig=unfinishedGig)
                savedFeatures = Feature.objects.filter(gig=unfinishedGig)
                self.deleteSavedEntities(savedPackages)
                self.deleteSavedEntities(savedFeatures)

                # Assign packages tier
                i = 1
                for eachPackage in packageFormset:
                    package = eachPackage.save(commit=False)
                    if i == 1:
                        package.tier = 'B'
                        i += 1
                    elif i == 2:
                        package.tier = 'N'
                        i += 1
                    elif i == 3:
                        package.tier = 'P'
                    else:
                        pass
                    # Assign package to the gear and save
                    package.gig = unfinishedGig
                    package.save()
                # Assign non blank features to gig and save
                i = 0
                for eachFeature in featuresFormset:
                    # Don't know excactly how django handles this, but this
                    # will break the loop in case a malicious actor wants to
                    # create an absourd ammount of features.
                    if i > 9:
                        break
                    i += 1
                    if any(eachFeature.cleaned_data.values()):
                        feature = eachFeature.save(commit=False)
                        feature.gig = unfinishedGig
                        feature.save()
            else:
                # If it's not valid, return the page with errors.
                context = {'packageFormset': packageFormset,
                           'featuresFormset': featuresFormset}
                return render(request, 'gigs/createPriceAndPackages.html', context=context)

        except:
            # If therre is no unfinished gig, go to the create gig page.
            return redirect('/gigs/create')

        # Everything went all rigth, go to extras.
        return redirect('/gigs/create/extras')

    def deleteSavedEntities(self, QuerySet):
        for eachEntity in QuerySet:
            eachEntity.delete()


class CreateExtrasView(View):

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        # Check if the user has an unfinished gig.
        try:
            unfinishedGig = Gig.objects.filter(
                author=request.user).get(isFinished=False)
            packages = Package.objects.filter(gig=unfinishedGig)
            if not any(list(packages)):
                return redirect('/gigs/create/packages/')
        except Exception as e:
            print(e)
            # If therre is no unfinished gig, go to the create gig page.
            return redirect('/gigs/create')

        # We use a formset to make it easier to validate if there is
        # no fast extra
        # Create the formset for the extras
        fastExtrasFormsetFactory = modelformset_factory(
            Extra, form=FastExtraForm, extra=1, max_num=1, min_num=0, validate_min=0)
        # Here we populate the formset with existing extras (if any)
        fastExtraFormset = fastExtrasFormsetFactory(
            queryset=Extra.objects.filter(gig=unfinishedGig).filter(isFast=True), prefix='FastExtras')
        # Create the formset for the extras
        extrasFormsetFactory = modelformset_factory(
            Extra, form=ExtraForm, extra=10, max_num=10, min_num=0, validate_min=0)
        # Here we populate the formset with existing extras (if any)
        extraFormset = extrasFormsetFactory(
            queryset=Extra.objects.filter(gig=unfinishedGig).filter(isFast=False), prefix='extras')

        context = {'extraFormset': extraFormset,
                   'fastExtraFormset': fastExtraFormset}
        return render(request, 'gigs/createExtras.html', context=context)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        # Check if the user has an unfinished gig.
        try:
            unfinishedGig = Gig.objects.filter(
                author=request.user).get(isFinished=False)
            packages = Package.objects.filter(gig=unfinishedGig)
            if not any(list(packages)):
                return redirect('/gigs/create/packages/')
        except:
            # If there is no unfinished gig, go to the create gig page.
            return redirect('/gigs/create')

        # We use an error to save as much valid data as we can
        # instead of warning each time a wrong form is found.

        error = False

        # First we deal with the single fast Extra
        # We use a formset to make it easier to validate if there is
        # no fast extra

        # Load the formsets
        fastExtrasFormsetFactory = modelformset_factory(
            Extra, form=FastExtraForm, extra=1, max_num=1, min_num=0, validate_min=0)
        # Populate with the request
        fastExtraFormset = fastExtrasFormsetFactory(
            request.POST, request.FILES, prefix='FastExtras')

        # Check if they are valid
        if fastExtraFormset.is_valid():
            # Delete all previous Fast Extras
            savedExtras = Extra.objects.filter(
                gig=unfinishedGig, isFast=True)
            self.deleteSavedEntities(savedExtras)

            i = 0
            for eachExtra in fastExtraFormset:
                # Don't know excactly how django handles this, but this
                # will break the loop in case a malicious actor wants to
                # create an absourd ammount of extras.
                if i > 1:
                    break
                i += 1
                # Assign non blank extras to gig and save
                if any(eachExtra.cleaned_data.values()):
                    extra = eachExtra.save(commit=False)
                    extra.gig = unfinishedGig
                    extra.title = 'Entrega Rápida'
                    extra.description = 'El freelancer entregará tu orden antes de la fecha original.'
                    extra.isFast = True
                    extra.save()
        else:
            error = True
        # Now the regular Extras.

        # Load the formsets
        extrasFormsetFactory = modelformset_factory(
            Extra, form=ExtraForm, extra=10, max_num=10, min_num=0, validate_min=0)
        # Populate with the request
        extraFormset = extrasFormsetFactory(
            request.POST, request.FILES, prefix='extras')

        # Check if they are valid
        if extraFormset.is_valid():
            # Delete all previous non-Fast Extras
            savedExtras = Extra.objects.filter(
                gig=unfinishedGig, isFast=False)
            self.deleteSavedEntities(savedExtras)

            i = 0
            for eachExtra in extraFormset:
                # Don't know excactly how django handles this, but this
                # will break the loop in case a malicious actor wants to
                # create an absourd ammount of extras.
                if i > 9:
                    break
                i += 1
                # Assign non blank extras to gig and save
                if any(eachExtra.cleaned_data.values()):
                    extra = eachExtra.save(commit=False)
                    extra.gig = unfinishedGig
                    extra.save()
        else:
            error = True
        # If there was an error while saving and validating, render the form
        if error:
            context = {'extraFormset': extraFormset,
                       'fastExtraFormset': fastExtraFormset}
            return render(request, 'gigs/createExtras.html', context=context)
        # If we got here, everything went all rigth, go to FAQs
        return redirect('/gigs/create/FAQs')

    def deleteSavedEntities(self, QuerySet):
        for eachEntity in QuerySet:
            eachEntity.delete()


class CreateRequirementsView(View):

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        # Check if the user has an unfinished gig.
        try:
            unfinishedGig = Gig.objects.filter(
                author=request.user).get(isFinished=False)
            # We need to make sure they at least have a saved package set
            packages = Package.objects.filter(gig=unfinishedGig)
            if not any(list(packages)):
                return redirect('/gigs/create/packages/')
        except:
            # If there is no unfinished gig, go to the create gig page.
            return redirect('/gigs/create')

        # Create the formset for the Requirements
        RequirementsFormsetFactory = modelformset_factory(
            Requirement, form=RequirementForm, extra=10, max_num=10, min_num=0, validate_min=0)
        # Here we populate the formset with existing FAQs (if any)
        RequirementsFormset = RequirementsFormsetFactory(
            queryset=Requirement.objects.filter(gig=unfinishedGig), prefix='Requirements')

        context = {'RequirementsFormset': RequirementsFormset}
        return render(request, 'gigs/createRequirements.html', context=context)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        # Check if the user has an unfinished gig.
        try:
            unfinishedGig = Gig.objects.filter(
                author=request.user).get(isFinished=False)
            # We need to make sure they at least have a saved package set
            packages = Package.objects.filter(gig=unfinishedGig)
            if not any(list(packages)):
                return redirect('/gigs/create/packages/')
        except:
            # If there is no unfinished gig, go to the create gig page.
            return redirect('/gigs/create')

        # Load the formsets
        requirementsFormsetFactory = modelformset_factory(
            Requirement, form=RequirementForm, extra=10, max_num=10, min_num=0, validate_min=0)
        # Populate with the request
        RequirementsFormset = requirementsFormsetFactory(
            request.POST, request.FILES, prefix='Requirements')

        # Check if they are valid
        if RequirementsFormset.is_valid():
            # Delete all previous non-Fast Extras
            savedRequirements = Requirement.objects.filter(
                gig=unfinishedGig)
            self.deleteSavedEntities(savedRequirements)

            i = 0
            for eachRequirement in RequirementsFormset:
                # Don't know excactly how django handles this, but this
                # will break the loop in case a malicious actor wants to
                # create an absourd ammount of extras.
                if i > 9:
                    break
                i += 1
                # Assign non blank extras to gig and save
                if any(eachRequirement.cleaned_data.values()):
                    requirement = eachRequirement.save(commit=False)
                    requirement.gig = unfinishedGig
                    requirement.save()
        else:
            # If there was an error while saving and validating, render the form
            context = {'RequirementsFormset': RequirementsFormset}
            return render(request, 'gigs/createFAQs.html', context=context)

        # If we got here, we have everything we need to post the gig
        return self.postGig(unfinishedGig)

    def postGig(self, unfinishedGig):
        features = Feature.objects.filter(gig=unfinishedGig)
        packages = Package.objects.filter(gig=unfinishedGig)
        # We add all the features available for each package
        for eachPackage in packages:
            if eachPackage.tier == 'B':
                eachPackage.features.add(*list(features.filter(tier1=True)))
            elif eachPackage.tier == 'N':
                eachPackage.features.add(*list(features.filter(tier2=True)))
            else:
                eachPackage.features.add(*list(features.filter(tier3=True)))
            eachPackage.save()
        # Activate the package
        unfinishedGig.isFinished = True
        unfinishedGig.isActive = True
        unfinishedGig.save()
        # Redirect to the (now finished) gig's page
        return redirect(unfinishedGig.get_absolute_url())

    def deleteSavedEntities(self, QuerySet):
        for eachEntity in QuerySet:
            eachEntity.delete()


class CreateFAQsView(View):

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        # Check if the user has an unfinished gig.
        try:
            # If he does, get the FAQs asociated with it.
            unfinishedGig = Gig.objects.filter(
                author=request.user).get(isFinished=False)
        except:
            # If there is no unfinished gig, go to the create gig page.
            return redirect('/gigs/create')

        # Create the formset for the FAQs
        FAQsFormsetFactory = modelformset_factory(
            FAQ, form=FAQsForm, extra=10, max_num=10, min_num=0, validate_min=0)
        # Here we populate the formset with existing FAQs (if any)
        FAQsFormset = FAQsFormsetFactory(
            queryset=FAQ.objects.filter(gig=unfinishedGig), prefix='FAQs')

        context = {'FAQsFormset': FAQsFormset}
        return render(request, 'gigs/createFAQs.html', context=context)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        # Check if the user has an unfinished gig.
        try:
            unfinishedGig = Gig.objects.filter(
                author=request.user).get(isFinished=False)
        except:
            # If there is no unfinished gig, go to the create gig page.
            return redirect('/gigs/create')

        # Load the formsets
        FAQsFormsetFactory = modelformset_factory(
            FAQ, form=FAQsForm, extra=10, max_num=10, min_num=0, validate_min=0)
        # Populate with the request
        FAQsFormset = FAQsFormsetFactory(
            request.POST, request.FILES, prefix='FAQs')

        # Check if they are valid
        if FAQsFormset.is_valid():
            # Delete all previous non-Fast Extras
            savedFAQs = FAQ.objects.filter(
                gig=unfinishedGig)
            self.deleteSavedEntities(savedFAQs)

            i = 0
            for eachFAQ in FAQsFormset:
                # Don't know excactly how django handles this, but this
                # will break the loop in case a malicious actor wants to
                # create an absourd ammount of extras.
                if i > 9:
                    break
                i += 1
                # Assign non blank extras to gig and save
                if any(eachFAQ.cleaned_data.values()):
                    faq = eachFAQ.save(commit=False)
                    faq.gig = unfinishedGig
                    faq.save()
        else:
            # If there was an error while saving and validating, render the form
            context = {'FAQsFormset': FAQsFormset}
            return render(request, 'gigs/createFAQs.html', context=context)

        # If we got here, everything went all rigth, go to FAQs
        return redirect('/gigs/create/requirements')

    def deleteSavedEntities(self, QuerySet):
        for eachEntity in QuerySet:
            eachEntity.delete()


class detailedGig(View):
    def get(self, request, *args, **kwargs):
        gig = get_object_or_404(
            Gig, pk=kwargs['id'])
        if gig.isFinished and gig.isActive:
            packages = Package.objects.filter(gig=gig)
            features = Feature.objects.filter(gig=gig)
            extras = Extra.objects.filter(gig=gig)
            requirements = Requirement.objects.filter(gig=gig)
            faqs = FAQ.objects.filter(gig=gig)
            author = UserProfile.objects.get(user=gig.author)
            extrasForms = []
            for i, eachExtra in enumerate(extras):
                if eachExtra.isFast:
                    extrasForms.append(FastExtraOrder(
                        extra=eachExtra, prefix='extra_%s' % i))
                else:
                    extrasForms.append(ExtraOrder(
                        extra=eachExtra, prefix='extra_%s' % i))

            context = {'gig': gig, 'packages': packages, 'features': features,
                       'extras': extrasForms, 'requirements': requirements, 'faqs': faqs,
                       'author': author}
            return render(request, 'gigs/detailedGig.html', context=context)
        else:
            return render(request, 'theme/404.html')

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        # Get the order details from the request
        orderDetails = self.get_selected_options(request, kwargs)

        if orderDetails != None:
            return redirect('checkout', orderDetails=OrderDecoder.encode(orderDetails))

        raise Http404

    def get_selected_options(self, request, kwargs):
        # Initialize as none because we check if everything went ok after returning the object
        orderDetails = None
        # Search for the gig
        gig = get_object_or_404(Gig, pk=kwargs['id'])
        # Procced only if it is active and finished
        if gig.isFinished and gig.isActive:
            # Get the selected package and the extras
            if 'B' in request.POST:
                package = Package.objects.filter(gig=gig).get(tier='B')
            elif 'N' in request.POST:
                package = Package.objects.filter(gig=gig).get(tier='N')
            else:
                package = Package.objects.filter(gig=gig).get(tier='P')

            extras = Extra.objects.filter(gig=gig)

            # This will be the array where we will store the forms gathered
            # from the post request
            extrasForms = []
            # This will bound the forms with the request and add them to the array
            for i, eachExtra in enumerate(extras):
                # Fast Extras get a different form
                if eachExtra.isFast:
                    extrasForms.append(FastExtraOrder(request.POST,
                                                      extra=eachExtra, prefix='extra_%s' % i))
                else:
                    extrasForms.append(ExtraOrder(request.POST,
                                                  extra=eachExtra, prefix='extra_%s' % i))
            # The checkout view uses a different form for the extras, stored in a different array
            selectedExtras = []
            # If the post form is valid, add the extras to the array as a tuple with the following
            # structure:
            # ( Number_of_times_selected, extra  )
            for i, eachForm in enumerate(extrasForms):

                if eachForm.is_valid():
                    if 'B' in request.POST:
                        if int(eachForm.cleaned_data['extra_B']) > 0:
                            selectedExtras.append(
                                (eachForm.cleaned_data['extra_B'], eachForm.extra))
                    elif 'N' in request.POST:
                        if int(eachForm.cleaned_data['extra_N']) > 0:
                            selectedExtras.append(
                                (eachForm.cleaned_data['extra_N'], eachForm.extra))
                    else:
                        if int(eachForm.cleaned_data['extra_P']) > 0:
                            selectedExtras.append(
                                (eachForm.cleaned_data['extra_P'], eachForm.extra))

            orderDetails = {}
            orderDetails['package'] = package
            orderDetails['selectedExtras'] = selectedExtras
        return orderDetails


class OrderCheckoutView(View):

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        # Convert the order string from the url to dict
        context = OrderDecoder.decode(kwargs['orderDetails'])
        # get al necesary parameters
        context['deliveryDate'] = PackageCalculator.getDeliveryDate(
            context['package'], context['selectedExtras'])
        requirements = list(Requirement.objects.filter(
            gig=context['package'].gig))
        context['requirements'] = requirements
        features = list(Feature.objects.filter(
            gig=context['package'].gig))
        context['features'] = ListFeatures.formatFeaturesfromPackage(
            context['package'], features)
        context['author'] = UserProfile.objects.get(
            user=context['package'].gig.author)
        context['totalPrice'] = PackageCalculator.getTotalPrice(
            context['package'], context['selectedExtras'])
        context['extrasPrice'] = PackageCalculator.getExtrasPrice(
            context['package'], context['selectedExtras'])

        return render(request, 'gigs/checkout.html', context=context)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        # Convert the order string from the url to dict
        orderDetails = OrderDecoder.decode(kwargs['orderDetails'])
        # this is done just as a sanity check
        return redirect('pay', orderDetails=OrderDecoder.encode(orderDetails))


class OrderPayment(View):

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        # Convert the order string from the url to dict
        context = OrderDecoder.decode(kwargs['orderDetails'])
        # get al necesary parameters
        context['totalPrice'] = PackageCalculator.getTotalPrice(
            context['package'], context['selectedExtras'])
        context['extrasPrice'] = PackageCalculator.getExtrasPrice(
            context['package'], context['selectedExtras'])

        return render(request, 'gigs/pay.html', context=context)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        # Process the order
        order = OrderManager.processOrder(request, kwargs['orderDetails'])

        if order is None:
            raise SomethingWrongException(
                'There was a problem while processing your order')

        return redirect('req', orderID=order.orderID)


class OrderPayment(View):

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        # Convert the order string from the url to dict
        context = OrderDecoder.decode(kwargs['orderDetails'])
        # get al necesary parameters
        context['totalPrice'] = PackageCalculator.getTotalPrice(
            context['package'], context['selectedExtras'])
        context['extrasPrice'] = PackageCalculator.getExtrasPrice(
            context['package'], context['selectedExtras'])

        return render(request, 'gigs/pay.html', context=context)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        # Process the order
        order = OrderManager.processOrder(request, kwargs['orderDetails'])

        if order is None:
            raise SomethingWrongException(
                'There was a problem while processing your order')

        return redirect('req-thanks', orderID=order.orderID, thanks=True)
