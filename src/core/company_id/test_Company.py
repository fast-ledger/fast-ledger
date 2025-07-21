from company_id import CompanyID

# 假設處理完所有 QR code 並擷取統編
tax_id_list = ['54757116', '88398574', '24511257']

# 確保最新檔案
CompanyID.fetch_sheet()

# 查詢公司對應資訊
company_info = CompanyID.extract_multiple_taxids(tax_id_list)

# 顯示結果
# for info in company_info:
print(company_info)