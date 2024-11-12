from apps.gigs.models import Order
from apps.gigs.utils import OrderDecoder, PackageCalculator


def set_order_fee(order):
    # TODO: Change percentage to dynamic
    order.feePercentage = 15


class OrderManager(object):
    @staticmethod
    def processOrder(request, orderString):
        # Convert the order string from the url to dict
        # this is done just as a sanity check
        orderDetails = OrderDecoder.decode(orderString)

        # Create the new order
        order = Order()

        # TODO: check if the order has been paid
        # order.payed=true

       # Populate with the detaiils
        order.orderString = orderString
        order.buyer = request.user
        order.seller = orderDetails['package'].gig.author
        order.price = PackageCalculator.getTotalPrice(
            orderDetails['package'], orderDetails['selectedExtras'])

        set_order_fee(order)

        order.save()

        # TODO: Notify freelancer

        return order
