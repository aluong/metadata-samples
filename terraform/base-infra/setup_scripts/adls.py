from azure.storage.blob import BlockBlobService

#################### Insert Information ######################

ACCOUNT_NAME = "<Insert Storage Account Name>"
ACCOUNT_KEY = "<Insert ADLS Primary Access Key>"
CONTAINER_NAME = "<Insert ADLS Container Name>"

##############################################################

try:
    blob_service = BlockBlobService(account_name=ACCOUNT_NAME, account_key=ACCOUNT_KEY)

    blob_service.create_blob_from_path(CONTAINER_NAME, "example_sales_folder/testdata.csv", "./adls_files/testdata.csv")
    blob_service.create_blob_from_path(CONTAINER_NAME, "dbo.exampletable.txt", "./adls_files/dbo.exampletable.txt")   

except Exception as error:
    print("Error:", error)

