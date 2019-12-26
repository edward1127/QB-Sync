from auth import client
from quickbooks.objects.bill import Bill
from quickbooks.objects.invoice import Invoice
from google_sheet_model import BILL_SHEET, INVOICE_SHEET, Entry, BillEntry, InvoiceEntry
from retrying import retry

# Retrieve data from QB API, and store them in specified Google Sheets via google_sheet_model.py


class DataProcess:
    def __init__(self, base_object, qb):
        self.qb = qb
        self.base_object = base_object
    # get all objects from QB API
    @retry(wait_fixed=110000)
    def get_all_objects(self):
        return self.base_object.all(qb=self.qb)
    # get all objects and turn them into dict form from QB API
    @retry(wait_fixed=110000)
    def get_all_objects_dict(self):
        data_list = []
        for object in self.get_all_objects():
            data_list.append(object.to_dict())
        return data_list
    # get custom field data in dict
    @staticmethod
    def get_custom_field(item):
        CustomField_result = ''
        CustomField_len = len(item.get('CustomField'))
        if item.get('CustomField') is not None:
            for CustomField in item.get('CustomField')[0:]:
                CustomField_result += "{}:{}".format(CustomField.get('Name'),
                                                     CustomField.get('StringValue')) + "\n"
            return CustomField_result.rstrip()
        return CustomField_result
    # compare two lists and remove the duplicates in l1 return l1 without any duplicates
    @staticmethod
    def remove_duplicate_in_l1(l1, l2):
        temp = []
        for item in l1:
            if item not in l2:
                temp.append(item)
        return temp


class BillDataProcess(DataProcess):
    def __init__(self, base_object=Bill, qb=client):
        super().__init__(base_object, qb)
    '''
     retrieve all Bill Objects in Dict form from QB API. If the Id from api can match the one in the sheet, 
     update it. Otherwise add it to a new row. Also, If a Bill object is deleted from QB, the coresponding one
     in the sheet will also be deleted. 
     required parametered: sheet to be updated 
    '''
    @retry(wait_fixed=110000)
    def full_sync(self, sheet):
        # get all Ids from first col in the sheet
        Id_list = sheet.col_values(1)
        # get all Bills in dict from QB_API
        items = self.get_all_objects_dict()
        Id_list_from_items = []
        for item in self.get_all_objects_dict():
            Id = item.get('Id')
            Id_list_from_items.append(Id)
            # create a BillEntry object
            new_entry = BillEntry(
                Id=Id,
                Date=item.get('TxnDate'),
                Type=item.get('LinkedTxn')[0].get('TxnType') if len(
                    item.get('LinkedTxn')) > 0 else "",
                Po_No=item.get('DocNumber'),
                Payee=item.get('VendorRef').get('name') if item.get(
                    'VendorRef') is not None else "",
                Due_Date=item.get('DueDate'),
                Balance=item.get('Balance'),
                Total=item.get('TotalAmt'),
                SyncToken=item.get('SyncToken')
            )
            # Id already in the sheet, update it
            if Id in Id_list:
                new_entry.update_entry(sheet=sheet)
            # Id not in the sheet, add it
            else:
                new_entry.add_entry(sheet=sheet)
        # find Bill Ids deleted from QB and delete them in the sheet
        Id_list_after_updated = sheet.col_values(1)
        # get Ids which were deleted on QB
        Id_deleted = DataProcess.remove_duplicate_in_l1(Id_list_after_updated, Id_list_from_items)
        for Id in Id_deleted:
            if Id != 'Id':
                Entry.delete_row(Id=Id, sheet=sheet)


class InvoiceDataProcess(DataProcess):
    def __init__(self, base_object=Invoice, qb=client):
        super().__init__(base_object, qb)
    '''
     retrieve all Invoice Objects in Dict form from QB API. If the Id from api can match the one in the sheet, 
     update it. Otherwise add it to a new row. Also, If a Bill object is deleted from QB, the coresponding one
     in the sheet will also be deleted.
     required parametered: sheet to be updated 
    '''
    @retry(wait_fixed=110000)
    def full_sync(self, sheet):
        # get all Ids from first col in the sheet
        Id_list = sheet.col_values(1)
        # get all invoice in dict from QB_API
        items = self.get_all_objects_dict()
        Id_list_from_items = []
        for item in items:
            Id = item.get('Id')
            Id_list_from_items.append(Id)
            # create an InvoiceEntry object
            new_entry = InvoiceEntry(
                Id=Id,
                Date=item.get('TxnDate'),
                Customer_Po_No=item.get('DocNumber'),
                Customer=item.get('CustomerRef').get('name'),
                Due_Date=item.get('DueDate'),
                Balance=item.get('Balance'),
                Total=item.get('TotalAmt'),
                CustomField=DataProcess.get_custom_field(item),
                SyncToken=item.get('SyncToken')
            )
            # Id already in the sheet, update it
            if Id in Id_list:
                new_entry.update_entry(sheet=sheet)
            # Id not in the sheet, add it
            else:
                new_entry.add_entry(sheet=sheet)
        # find Invoice Ids deleted from QB and delete them in the sheet
        Id_list_after_updated = sheet.col_values(1)
        # get Ids which were deleted on QB
        Id_deleted = DataProcess.remove_duplicate_in_l1(Id_list_after_updated, Id_list_from_items)
        for Id in Id_deleted:
            if Id != 'Id':
                Entry.delete_row(Id=Id, sheet=sheet)


BillDataProcess().full_sync(sheet=BILL_SHEET)
InvoiceDataProcess().full_sync(sheet=INVOICE_SHEET)

