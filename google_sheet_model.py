import gspread
import os
import random
from retrying import retry
from oauth2client.service_account import ServiceAccountCredentials

'''
Get creds from env vars, and then open the specifying sheet.
'''

def create_keyfile_dict():
    variables_keys = {
        "type": os.getenv("SHEET_TYPE"),
        "project_id": os.getenv("SHEET_PROJECT_ID"),
        "private_key_id": os.getenv("SHEET_PRIVATE_KEY_ID"),
        "private_key": os.getenv("SHEET_PRIVATE_KEY"),
        "client_email": os.getenv("SHEET_CLIENT_EMAIL"),
        "client_id": os.getenv("SHEET_CLIENT_ID"),
        "auth_uri": os.getenv("SHEET_AUTH_URI"),
        "token_uri": os.getenv("SHEET_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("SHEET_AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.getenv("SHEET_CLIENT_X509_CERT_URL")
    }
    return variables_keys


scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    create_keyfile_dict(), scope)

client = gspread.authorize(creds)

# Open the Test_Sheet
# BILL_SHEET = client.open("QuickBooks").worksheet("Expenses")
# INVOICE_SHEET = client.open("QuickBooks").worksheet("Invoice")
# TOKEN_SHEET = client.open("Token").worksheet("Token")

# Open the Production_Sheet
BILL_SHEET = client.open("DataSync").worksheet("QB-Bill")
INVOICE_SHEET = client.open("DataSync").worksheet("QB-Invoice")
TOKEN_SHEET = client.open("Token").worksheet("QB_Token")


class Entry:
    def __init__(self, Id=''):
        self.Id = Id

    @retry(wait_fixed=110000)
    def add_entry(self, sheet):
        sheet.append_row(list(vars(self).values()))
        print('Added: {}'.format(self.Id))

    @retry(wait_fixed=110000)
    def update_entry(self, sheet):
        # find the row to update
        col_headers = sheet.row_values(1)
        row_to_update = sheet.find("{}".format(self.Id)).row
        last_col_A1_notation = Entry.colnum_to_string(len(col_headers))
        cell_list = sheet.range('A{}:{}{}'.format(
            row_to_update, last_col_A1_notation, row_to_update))
        for i in range(len(col_headers)):
            cell_list[i].value = getattr(self, col_headers[i], '')
        sheet.update_cells(cell_list)
        print('Updated Id: {}'.format(self.Id))

    @staticmethod
    @retry(wait_fixed=110000)
    def delete_row(Id, sheet):
        row_to_delete = sheet.find("{}".format(Id)).row
        sheet.delete_row(row_to_delete)
        print('Deleted Id: {}'.format(Id))

    @staticmethod
    def colnum_to_string(n):
        string = ""
        while n > 0:
            n, remainder = divmod(n - 1, 26)
            string = chr(65 + remainder) + string
        return string


class BillEntry(Entry):

    def __init__(self, Id='', Date='', Type='', Po_No='', Payee='', Category='', Due_Date='', Balance='',
                 Total='', SyncToken=''):
        super().__init__(Id)
        self.Date = Date
        self.Type = Type
        self.Po_No = Po_No
        self.Payee = Payee
        self.Due_Date = Due_Date
        self.Balance = Balance
        self.Total = Total
        self.SyncToken = SyncToken


class InvoiceEntry(Entry):

    def __init__(self, Id='', Date='', Type='', Customer_Po_No='', Customer='', Due_Date='', Balance='',
                 Total='', CustomField='', SyncToken=''):

        super().__init__(Id)
        self.Date = Date
        self.Customer_Po_No = Customer_Po_No
        self.Customer = Customer
        self.Due_Date = Due_Date
        self.Balance = Balance
        self.Total = Total
        self.CustomField = CustomField
        self.SyncToken = SyncToken
