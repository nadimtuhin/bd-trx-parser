"""Sanitized SMS bodies modelled on real alerts.

Every account, card, phone number, name and transaction id here is fake or masked.
"""

# ── EBL ─────────────────────────────────────────────────────────────────────
EBL_SAVINGS_CREDIT_BEFTN = (
    "AC 101***111 is credited with BDT 25,000.00 BEFTN Inward from ACME TRADING LTD. "
    "Balance is BDT 1,02,345.67. EBL"
)
EBL_SAVINGS_DEBIT_NPSB = (
    "AC 101***111 is debited with BDT 2,000.00 NPSB Fund Transfer to 1234****5678. Balance is BDT 98,765.43"
)
EBL_SAVINGS_DEBIT_NO_DESCRIPTION = "AC 202***222 is debited with BDT 500. Balance is BDT 9,500.00"
EBL_DEBIT_CARD_PURCHASE = (
    "Purchase txn BDT 6,000.00 from GREEN LEAF CAFE DHAKA.Card 422222**2222 on 30-Sep-26 14:22. "
    "Your A/C 101***111 Balance BDT 45,000.00"
)
EBL_DEBIT_CARD_PURCHASE_DOTTED_MERCHANT = (
    "Purchase txn BDT 1,499 from DARAZ.COM.BD.Card 422222**2222 on 01-Oct-26 09:10."
)
EBL_CREDIT_CARD_BDT_PURCHASE = (
    "EBL CARDS: Purchase txn BDT 1,250.50 from SHOPNO SUPERSTORE. Card 411111**1111 on 02-Oct-26. "
    "Balance: BDT 14,750.50"
)
EBL_CREDIT_CARD_USD_PURCHASE = (
    "EBL CARDS: Purchase txn USD 15.99 from NETFLIX.COM.Card 411111**1111 on 03-Oct-26."
)
EBL_CREDIT_CARD_LEGACY_LAYOUT = "EBL CARDS: POS txn BDT 500.00 using Card 411111**1111 at CAFE 21"
EBL_CREDIT_CARD_USD_PAYMENT = "EBL CARDS: Payment of USD 120.00 credited to Card 411111**1111 on 05-Oct-26."
EBL_CREDIT_CARD_USD_REVERSAL = (
    "EBL CARDS: Purchase transaction USD 15.99 has been reversed to card 411111**1111."
)
EBL_ATM_WITHDRAWAL = (
    "Cash WD BDT5000 from EBL GULSHAN BRANCH ATM. Card 422222**2222 on 06-Oct-26 20:01. "
    "Your A/C 101***111 Balance BDT 40,000.00"
)
EBL_OTP = "Your EBL OTP is 123456. Do not share it with anyone."

# ── DBBL ────────────────────────────────────────────────────────────────────
DBBL_ATM_WITHDRAWAL = (
    "Dear Customer, your A/C ***1234 debited (ATM Cash Withdrawal) by Tk5,000.00 on 12-Oct-26 10:22:11. "
    "C/B Tk12,345.67"
)
DBBL_POS_REMOTE_ON_US = (
    "Dear Customer, your A/C ***1234 debited (POS Purchase Remote On Us) by Tk850.00 on 12-Oct-26 13:00:02. "
    "C/B Tk11,495.67"
)
DBBL_POS = "Dear Customer, your A/C ***1234 debited (POS Purchase) by Tk1,200.50 on 13-Oct-26. C/B Tk10,295.17"
DBBL_CREDIT = (
    "Dear Customer, your A/C ***1234 credited (Fund Transfer) by Tk1,00,000.00 on 14-Oct-26. C/B Tk1,10,295.17"
)
DBBL_CREDIT_NO_DESCRIPTION = "Dear Customer, your A/C ***1234 credited by Tk1,000.00 on 14-Oct-26. C/B Tk2,000.00"

# ── City Bank ───────────────────────────────────────────────────────────────
CITY_WITHDRAWAL_LINES = (
    "12-Oct-2026\nCitytouch Fund Transfer\nTk. 5,000.00 Withdrawal\nTk. 20,345.50 Balance\nA/C: 9900***0042"
)
CITY_DEPOSIT_LINES = (
    "13-Oct-2026\r\nSalary ACME LTD\r\nTk. 80,000.00 Deposit\r\nTk. 1,00,345.50 Balance\r\nA/C: 9900***0042"
)
CITY_PURCHASE_LINES_WITH_RATE = (
    "14-Oct-2026\nUSD rate 122.50\nAMAZON WEB SERVICES\nTk. 1,225.00 Purchased\nTk. 99,120.50 Balance\nA/C: 9900***0042"
)
CITY_CREDITED_SENTENCE = (
    "Tk. 2,500.00 credited to A/C 9900***0042 by Citytouch transfer from 1781***2210. Balance Tk. 3,000.00"
)
CITY_DEBITED_SENTENCE = "Tk. 1,000.00 has been debited from your A/C: 9900***0042 for bKash transfer."

# ── City AMEX ───────────────────────────────────────────────────────────────
AMEX_PURCHASE = (
    "Tk. 3,634.00 purchased at RANG BANGLADESH LTD JAMUNA FUT\nCARD NO: 371***999\nBal Tk. 1,20,000.00"
)
AMEX_PURCHASE_BDT_ONE_LINE = "BDT 2,000.00 purchased at UNIMART GULSHAN CARD NO: 371***999 Bal BDT 98,000.00"
AMEX_PURCHASE_WITH_DATE = "BDT 1,816.00 purchased at SHOP NAME on 25-Oct-26. CARD NO: 371***999. Bal BDT 780,554.82."
AMEX_PAYMENT_RECEIVED = "Tk. 28,260.00 payment received\nCARD NO: 371***999"
AMEX_PAYMENT_OF = "Payment of BDT 28,260.00 received for AMEX CARD NO: 371***999. Thank you."

# ── AIBL ────────────────────────────────────────────────────────────────────
AIBL_DEBIT = (
    "Your A/C 100200****300 has been Debited by BDT 2,750.00 on 12-OCT-26. Ref: FT26285ABCD. "
    "Balance: BDT 45,678.90"
)
AIBL_CREDIT_SHORT = "A/C 100200****300 Credited BDT 10,000.00 on 13-OCT-26. Balance: 55,678.90"
AIBL_TRANSFER_FROM = "Tk. 5000 has been Transfered from A/C: 100200****300 to DPS A/C."
AIBL_TRANSFER_TO = "Tk. 1,500.00 has been Transferred to A/C: 100200****300."

# ── bKash ───────────────────────────────────────────────────────────────────
BKASH_PAYMENT = (
    "Payment Tk 300.00 to SHOPNO-RM12345 successful. Fee Tk 0.00. Balance Tk 1,234.56. "
    "TrxID AB12CD34EF at 12/10/2026 13:45"
)
BKASH_PAYMENT_OF_IS = (
    "Payment of Tk 50.00 to Grameenphone Ltd-MyGP is successful. Balance Tk 1,184.56. TrxID GH56IJ78KL"
)
BKASH_SEND_MONEY = (
    "Send Money Tk 500.00 to 01912****77 successful. Ref rent. Fee Tk 5.00. Balance Tk 679.56. "
    "TrxID MN90OP12QR at 12/10/2026 14:00"
)
BKASH_CASH_OUT = (
    "Cash Out Tk 1,000.00 to 01712****99 successful. Fee Tk 18.50. Balance Tk 2,345.00. TrxID ST34UV56WX"
)
BKASH_CASH_IN = "Cash In Tk 2,000.00 from 01812****88 successful. Fee Tk 0.00. Balance Tk 4,345.00. TrxID YZ78AB90CD"
BKASH_RECEIVED = (
    "You have received Tk 10,000.00 from 01800****02. Ref family. Fee Tk 0.00. Balance Tk 15,234.56. "
    "TrxID EF12GH34IJ at 12/10/2026 18:30"
)
BKASH_REMITTANCE = (
    "You have received remittance.\nAmount: Tk 36,597.11\nSender: JOHN DOE\nCountry: UAE\nTrxID: KL56MN78OP"
)
BKASH_GOVT_INCENTIVE = (
    "You have received govt. incentive for remittance.\nIncentive Amount: Tk 914.93\nTrxID: QR90ST12UV"
)
BKASH_RECHARGE = "Received Recharge request of Tk 400.00 for 01700****01. Balance Tk 1,000.00. TrxID WX34YZ56AB"
BKASH_BILL = (
    "Bill successfully paid.\nBiller: DESCO (POSTPAID)\nA/C: 12****78\nAmount: Tk 2,910.00\n"
    "Fee: Tk 0.00\nTrxID: CD78EF90GH\nBalance: Tk 3,090.00"
)
BKASH_RECHARGE_FAILED = "Mobile Recharge request has failed. Tk 108.00 returned to your bKash account."
BKASH_CASHBACK = "You have received Cashback Tk 67.30 for Payment to SHOPNO. Balance Tk 1,301.86."
BKASH_BANK_DEPOSIT = (
    "You have received deposit from iBanking of Tk 2,500.00 from Pubali Bank. Fee Tk 0.00. "
    "Balance Tk 3,801.86. TrxID IJ12KL34MN"
)
BKASH_PROMO = "Get 10% cashback on your next Payment with bKash! T&C apply."

# ── Midland ─────────────────────────────────────────────────────────────────
MIDLAND_CARD_USE = (
    "Thanks for using MDB Visa Card# 455555*5555 for BDT 1,050.00 at APON FAMILY MART on 11-Oct-2026 18:30. "
    "Balance is BDT 23,456.00"
)
MIDLAND_PURCHASE_TXN = "MDB: Purchase txn BDT 2,300.00 from DARAZ BD. Card# 455555*5555 on 12-Oct-2026."
MIDLAND_PAYMENT = "BDT 3,000.00 has been credited to your Card# 455555*5555. Thank you for banking with MDB."
MIDLAND_BILL = (
    "Dear Cardmember, your MDB Card# 455555*5555 bill on 15-Oct-2026 is BDT 12,345.00 Dr. "
    "Min due BDT 617.00. Due date 05-Nov-2026."
)

# ── PathaoPay ───────────────────────────────────────────────────────────────
PATHAO_PAID = "Paid to Pathao Food.\nAmount BDT 938.00 Fee BDT 0.00\nBalance BDT 1,062.00\nTxn ID: PP12345678"
PATHAO_PAID_ONE_LINE = "Paid to Pathao Parcel. Amount BDT 120.00 Fee BDT 0.00 Balance BDT 942.00"

# ── Nagad ───────────────────────────────────────────────────────────────────
NAGAD_MONEY_RECEIVED = (
    "Money Received.\nAmount: Tk 1,500.00\nSender: 01712****99\nRef: N/A\nTxnID: 73ABCD12\n"
    "Balance: Tk 2,345.67\n12/10/2026 14:05"
)
NAGAD_CASH_IN = (
    "Cash In Successful.\nAmount: Tk 3,000.00\nUddokta: 01812****88\nTxnID: 73EFGH34\nBalance: Tk 5,345.67"
)
NAGAD_CASH_OUT = (
    "Cash Out Successful.\nAmount: Tk 1,000.00\nUddokta: 01912****77\nTxnID: 73IJKL56\nCharge: Tk 12.50\n"
    "Balance: Tk 4,333.17"
)
NAGAD_SEND_MONEY = (
    "Send Money Successful.\nAmount: Tk 500.00\nReceiver: 01612****66\nRef: rent\nTxnID: 73MNOP78\n"
    "Charge: Tk 5.00\nBalance: Tk 3,828.17"
)
NAGAD_OTP = "Your Nagad verification code is 482910. It expires in 2 minutes."
