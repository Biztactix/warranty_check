import sys
import time
import random
import requests

from shared import DEBUG, RETRY, ORDER_NO_TYPE

try:
    requests.packages.urllib3.disable_warnings()
except:
    pass


class Dell:
    def __init__(self, params):
        self.url = params['url']
        self.api_key = params['api_key']
        self.debug = DEBUG
        self.retry = RETRY
        self.order_no = ORDER_NO_TYPE
        self.d42_rest = params['d42_rest']
        self.common = None

        if self.order_no == 'common':
            self.common = self.generate_random_order_no()

    @staticmethod
    def error_msg(msg):
        print '\n[!] HTTP error. Message was: %s' % str(msg)

    def run_warranty_check(self, inline_serials, retry=True):
        if self.debug:
            print '\t[+] Checking warranty info for Dell "%s"' % inline_serials
        timeout = 10
        payload = {'id': inline_serials, 'apikey': self.api_key, 'accept': 'Application/json'}

        try:
            resp = requests.get(self.url, params=payload, verify=True, timeout=timeout)
            msg = 'Status code: %s' % str(resp.status_code)
            if str(resp.status_code) == '401':
                print '\t[!] HTTP error. Message was: %s' % msg
                print '\t[!] waiting for 30 seconds to let the api server calm down :D'
                # suspecting blockage due to to many api calls. Put in a pause of 30 seconds and go on
                time.sleep(30)
                if retry:
                    print '\n[!] Retry'
                    self.run_warranty_check(inline_serials, False)
                else:
                    return None
            else:
                result = resp.json()
                return result
        except requests.RequestException as e:
            self.error_msg(e)
            return None

    def process_result(self, result, purchases):
        data = {}

        if 'AssetWarrantyResponse' in result:
            for item in result['AssetWarrantyResponse']:
                try:
                    warranties = item['AssetEntitlementData']
                    asset = item['AssetHeaderData']
                    product = item['ProductHeaderData']
                except IndexError:
                    if self.debug:
                        try:
                            msg = str(result['InvalidFormatAssets']['BadAssets'])
                            if msg:
                                print '\t\t[-] Error: Bad asset: %s' % msg
                        except Exception as e:
                            print e

                else:
                    if self.order_no == 'vendor':
                        order_no = asset['OrderNumber']
                    elif self.order_no == 'common':
                        order_no = self.common
                    else:
                        order_no = self.generate_random_order_no()

                    serial = asset['ServiceTag']

                    '''
                    For future implementation of registering the purchase date as a lifecycle event
                    Add a lifecycle event for the system
                    data.update({'date':ship_date})
                    data.update({'type':'Purchased'})
                    data.update({'serial_no':serial})
                    d42.upload_lifecycle(data)
                    data.clear()
                    '''

                    # We need check per warranty service item
                    for sub_item in warranties:
                        data.clear()
                        ship_date = asset['ShipDate'].split('T')[0]
                        product_id = product['ProductId']

                        data.update({'order_no': order_no})
                        if ship_date:
                            data.update({'po_date': ship_date})
                        data.update({'completed': 'yes'})

                        data.update({'vendor': 'Dell Inc.'})
                        data.update({'line_device_serial_nos': serial})
                        data.update({'line_type': 'contract'})
                        data.update({'line_item_type': 'device'})
                        data.update({'line_completed': 'yes'})

                        line_contract_id = sub_item['ItemNumber']
                        data.update({'line_notes': line_contract_id})
                        data.update({'line_contract_id': line_contract_id})

                        # Using notes as well as the Device42 API doesn't give back the line_contract_id,
                        # so notes is now used for identification
                        # Mention this to device42

                        service_level_group = sub_item['ServiceLevelGroup']
                        if service_level_group == -1 or service_level_group == 5 or service_level_group == 8:
                            contract_type = 'Warranty'
                        elif service_level_group == 8 and 'compellent' in product_id:
                            contract_type = 'Service'
                        elif service_level_group == 11 and 'compellent' in product_id:
                            contract_type = 'Warranty'
                        else:
                            contract_type = 'Service'
                        data.update({'line_contract_type': contract_type})
                        if contract_type == 'Service':
                            # Skipping the services, only want the warranties
                            continue

                        try:
                            # There's a max 32 character limit
                            # on the line service type field in Device42 (version 10.2.1)
                            service_level_description = left(sub_item['ServiceLevelDescription'], 32)
                            data.update({'line_service_type': service_level_description})
                        except:
                            pass

                        start_date = sub_item['StartDate'].split('T')[0]
                        end_date = sub_item['EndDate'].split('T')[0]

                        data.update({'line_start_date': start_date})
                        data.update({'line_end_date': end_date})

                        # update or duplicate? Compare warranty dates by serial, contract_id and end date
                        hasher = serial + line_contract_id + end_date

                        try:
                            d_start, d_end = purchases[hasher]
                            # check for duplicate state
                            if d_start == start_date and d_end == end_date:
                                print '\t[!] Duplicate found. Purchase ' \
                                      'for SKU "%s" and "%s" with end date "%s" ' \
                                      'is already uploaded' % (serial, line_contract_id, end_date)
                        except KeyError:
                            self.d42_rest.upload_data(data)
                            data.clear()

    @staticmethod
    def generate_random_order_no():
        order_no = ''
        for index in range(9):
            order_no += str(random.randint(0, 9))
        return order_no


def dates_are_the_same(dstart, dend, wstart, wend):
    if time.strptime(dstart, "%Y-%m-%d") == time.strptime(wstart, "%Y-%m-%d") and \
                    time.strptime(dend, "%Y-%m-%d") == time.strptime(wend, "%Y-%m-%d"):
        return True
    else:
        return False


def left(s, amount):
    return s[:amount]