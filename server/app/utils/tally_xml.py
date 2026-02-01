import datetime

def generate_tally_xml(data: dict):
    """
    Generates a simplified Tally XML for a Purchase Voucher.
    """
    invoice_no = data.get("invoice_number") or "NA"
    date_str = data.get("date") or datetime.date.today().strftime("%Y-%m-%d")
    date = date_str.replace("-", "")
    vendor = data.get("vendor_name") or "Cash"
    total = data.get("total_amount") or 0
    tax = data.get("tax_amount") or 0
    subtotal = data.get("subtotal") or (float(total) - float(tax))
    category = data.get("category") or "Direct Expenses"

    xml = f"""<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Import Data</TALLYREQUEST>
    </HEADER>
    <BODY>
        <IMPORTDATA>
            <REQUESTDESC>
                <REPORTNAME>Vouchers</REPORTNAME>
                <STATICVARIABLES>
                    <SVCURRENTCOMPANY>Company Name</SVCURRENTCOMPANY>
                </STATICVARIABLES>
            </REQUESTDESC>
            <REQUESTDATA>
                <TALLYMESSAGE xmlns:UDF="TallyUDF">
                    <VOUCHER VCHTYPE="Purchase" ACTION="Create" OBJVIEW="AccountingVoucherView">
                        <DATE>{date}</DATE>
                        <VOUCHERNUMBER>{invoice_no}</VOUCHERNUMBER>
                        <REFERENCE>{invoice_no}</REFERENCE>
                        <PARTYLEDGERNAME>{vendor}</PARTYLEDGERNAME>
                        <STATENAME>State</STATENAME>
                        <PERSISTEDVIEW>AccountingVoucherView</PERSISTEDVIEW>
                        
                        <!-- Party Ledger Credit -->
                        <ALLLEDGERENTRIES.LIST>
                            <LEDGERNAME>{vendor}</LEDGERNAME>
                            <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
                            <AMOUNT>{total}</AMOUNT>
                        </ALLLEDGERENTRIES.LIST>
                        
                        <!-- Expense Ledger Debit -->
                        <ALLLEDGERENTRIES.LIST>
                            <LEDGERNAME>{category}</LEDGERNAME>
                            <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
                            <AMOUNT>-{subtotal}</AMOUNT>
                        </ALLLEDGERENTRIES.LIST>
                        
                        <!-- GST Ledger Debit (Optional) -->
                        <ALLLEDGERENTRIES.LIST>
                            <LEDGERNAME>Input GST</LEDGERNAME>
                            <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
                            <AMOUNT>-{tax}</AMOUNT>
                        </ALLLEDGERENTRIES.LIST>
                    </VOUCHER>
                </TALLYMESSAGE>
            </REQUESTDATA>
        </IMPORTDATA>
    </BODY>
</ENVELOPE>"""
    return xml
