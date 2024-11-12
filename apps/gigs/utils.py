from apps.gigs.models import Gig, Package, Extra, Feature, FAQ
from django.shortcuts import get_object_or_404
from django.http import Http404
from datetime import datetime, timedelta

# This will encode and decode orders into strings or dictionaries.


class OrderDecoder():
    # The encoding has the next format:
    # Package_pk _ number_of_extras _  extra_i_pk _ extra_i_times_bought
    @staticmethod
    def encode(dictionary):
        # Create an array of strings because its the way of concattenating
        # strings with the best performance
        stringArray = []
        # First add the pk of the package
        stringArray.append(str(dictionary['package'].pk))
        # Then the number of extras
        stringArray.append(str(len(dictionary['selectedExtras'])))
        # Then ech extra and the number of times it was bought
        for eachExtra in dictionary['selectedExtras']:
            stringArray.append(str(eachExtra[1].pk))
            stringArray.append(str(eachExtra[0]))
        # Join them using -'
        encodedString = '_'.join(stringArray)
        return encodedString

    @staticmethod
    def decode(encodedString):
        orderDictionary = {}
        try:
            # The encoded string's values (pk of the db objects) are "_" separated, split them.
            stringArray = encodedString.split('_')
            # The packagee is always the first parameter
            orderDictionary['package'] = get_object_or_404(
                Package, pk=stringArray[0])
            # The maximum number of extras theree can be is 10
            if int(stringArray[1]) > 10:
                raise Http404
            # This is a vector of tupples, (times_bougth, extra)
            selectedExtras = []
            # Increments of two because there are two values per tuple
            for i in range(0, int(stringArray[1])*2, 2):
                # Add the tuple to the vector
                extra = get_object_or_404(Extra, pk=stringArray[2+i])
                if extra.isFast:
                    days = True
                else:
                    days = int(stringArray[2+i+1])
                selectedExtras.append(
                    (days, extra))
            orderDictionary['selectedExtras'] = selectedExtras
            return orderDictionary
        except:
            raise SomethingWrongException(
                'Something is wrong with your order.')


class PackageCalculator(object):

    @staticmethod
    def getDeliveryDate(package, extras):
        totalDays = 0
        totalDays += package.deliveryTime
        for eachTuple in extras:
            totalDays += eachTuple[0] * \
                eachTuple[1].get_days_for_tier(package.tier)
        deliveryDate = (datetime.today() + timedelta(days=totalDays))
        return deliveryDate.strftime('%d/%m/%Y')

    @staticmethod
    def getTotalPrice(package, extras):

        totalPrice = 0
        totalPrice += package.price

        for eachTuple in extras:
            totalPrice += eachTuple[0] * \
                eachTuple[1].get_price_for_tier(package.tier)

        return totalPrice

    @staticmethod
    def getExtrasPrice(package, extras):

        totalPrice = 0
        for eachTuple in extras:
            totalPrice += eachTuple[0] * \
                eachTuple[1].get_price_for_tier(package.tier)

        return totalPrice


class ListFeatures(object):
    @staticmethod
    def formatFeaturesfromPackage(package, features):
        includedFeatures = []
        for eachFeature in features:
            if eachFeature.is_included_in_tier(package.tier):
                includedFeatures.append(eachFeature)
        return includedFeatures


class SomethingWrongException(Exception):
    pass
