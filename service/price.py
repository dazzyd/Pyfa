#===============================================================================
# Copyright (C) 2010 Diego Duclos
#
# This file is part of pyfa.
#
# pyfa is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyfa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyfa.  If not, see <http://www.gnu.org/licenses/>.
#===============================================================================

import service
import eos.db
import eos.types
import time
from xml.dom import minidom

VALIDITY = 24*60*60  # Price validity period, 24 hours
REREQUEST = 4*60*60  # Re-request delay for failed fetches, 4 hours
TIMEOUT = 15*60  # Network timeout delay for connection issues, 15 minutes

class Price():

    @classmethod
    def fetchPrices(cls, prices):
        """Fetch all prices passed to this method"""

        # Dictionary for our price objects
        priceMap = {}
        # Check all provided price objects, and add invalid ones to dictionary
        for price in prices:
            if not price.isValid:
                priceMap[price.typeID] = price

        if len(priceMap) == 0:
            return

        # Set of items which are still to be requested from this service
        toRequest = set()

        # Compose list of items we're going to request
        for typeID in priceMap:
            # Get item object
            item = eos.db.getItem(typeID)
            # We're not going to request items only with market group, as eve-central
            # doesn't provide any data for items not on the market
            if item.marketGroupID:
                toRequest.add(typeID)

        # Do not waste our time if all items are not on the market
        if len(toRequest) == 0:
            return

        # This will store POST data for eve-central
        data = []

        # Base request URL
        baseurl = "http://www.ceve-market.org/api/marketstat"
        data.append(("usesystem", 30000142)) # Use Jita for market

        for typeID in toRequest:  # Add all typeID arguments
            data.append(("typeid", typeID))

        # Attempt to send request and process it
        try:
            len(priceMap)
            network = service.Network.getInstance()
            data = network.request(baseurl, network.PRICES, data)
            xml = minidom.parse(data)
            types = xml.getElementsByTagName("marketstat").item(0).getElementsByTagName("type")
            # Cycle through all types we've got from request
            for type in types:
                # Get data out of each typeID details tree
                typeID = int(type.getAttribute("id"))
                sell = type.getElementsByTagName("sell").item(0)
                # If price data wasn't there, set price to zero
                try:
                    percprice = float(sell.getElementsByTagName("percentile").item(0).firstChild.data)
                except (TypeError, ValueError):
                    percprice = 0

                # Fill price data
                priceobj = priceMap[typeID]
                priceobj.price = percprice
                priceobj.time = time.time() + VALIDITY
                priceobj.failed = None

                # delete price from working dict
                del priceMap[typeID]

        # If getting or processing data returned any errors
        except service.network.TimeoutError, e:
            # Timeout error deserves special treatment
            for typeID in priceMap.keys():
                priceobj = priceMap[typeID]
                priceobj.time = time.time() + TIMEOUT
                priceobj.failed = None
                del priceMap[typeID]
        except:
            # all other errors will pass and continue onward to the REREQUEST delay
            pass

        # if we get to this point, then we've got an error. Set to REREQUEST delay
        for typeID in priceMap.keys():
            priceobj = priceMap[typeID]
            priceobj.price = 0
            priceobj.time = time.time() + REREQUEST
            priceobj.failed = None
