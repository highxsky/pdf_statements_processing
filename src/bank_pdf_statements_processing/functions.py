import os
import pandas as pd
from PyPDF2 import PdfReader # to extract number of pages from PDF file
import camelot # camelot to read PDFs properly

def get_files_metadata(path):

    # global dictionary storing all the dataframes
    # first key as sample for readability purposes

    # structure will be: file_name: [file_path, extraction_date, account_number, number_of_pages]
    dict = {}

    for file in os.listdir(path):

        if file.endswith('.pdf'):

            # get the extraction date (YYYYMM format)
            extraction_date = file[0:6]

            # get the end position for the account number (by retrieving file extension .pdf, 4 chars)
            account_position_end = len(file) - 4
            # get the start position for the account number (account is 11 digits)
            account_position_start = account_position_end - 11
            # get the account number
            account_number = file[account_position_start:account_position_end]

            # get the file path and checks the number of pages
            file_path = os.path.join(path, file)
            number_of_pages = len(PdfReader(file_path).pages)

            dict[file] = [file_path, extraction_date, account_number, number_of_pages]

        else:
            None

    return dict

def read_first_page(pdf_file, table_areas_first_page, column_positions):

    # output will be a table list and first page will have index 0
    table = camelot.read_pdf(
        # define the encoding to utf-8, to manage characters such as 'é' or 'è' or 'à'
        encoding = 'utf-8',
        # where the data will be read from
        filepath = pdf_file,
        # read first page only
        pages = '1',
        # to detect the table, list with positions expressed in points 
        table_areas = table_areas_first_page,
        # to detect columns, list with positions expressed in points
        columns = column_positions,
        # stream to parse tables that have whitespaces between celles to simulate a table structure
        flavor = 'stream'
    )

    # table to dataframe
    first_page_df = table[0].df 
    # indicating page number
    first_page_df.loc[:, "file_page"] = 1 

    return first_page_df

def clean_dataframe(df):

    # assign column names
    df.columns = [ "transaction_date", "transaction", "del1", "debit", "credit", "del2", "file_page"]

    # drop unnecessary columns
    df.drop(
        columns = ['del1', 'del2'], 
        inplace=True
    )

    # reset indexes
    # inplace = True,m replace the current DF
    # drop = True, do not keep the original index as new DF column
    df.reset_index(
        inplace=True, 
        drop=True
    )

    # drops row IDs where transaction date is missing
    df.drop(
        df[df["transaction_date"] == ""].index, 
        inplace=True
    )

    for col in ["debit", "credit"]:

        # replace debit and credit '.' by a '' to manage the thousand units (e.g. 2,000 becomes 2000)
        df[col] = df[col].str.replace(pat='.', repl='', regex=False).astype(str)

        # replace debit and credit ',' by a '.' so it can then be interpreted as float type
        df[col] = df[col].str.replace(pat=',', repl='.', regex=False).astype(str)

        # transforms the column into a numerical column
        df[col] = pd.to_numeric(df[col]).fillna(0)

    df['amount'] = df['credit'] - df['debit']

    df = df.drop(columns = ['credit', 'debit'])

    # drops row IDs where transaction date is missing
    df.drop(
        df[df["amount"] == 0].index, 
        inplace=True
    )

    # Reset of the index, as otherwise they may refer to deleted rows
    # e.g. for 10 operations on a page, the PDF scan outputs 30 rows, as line returns within cells are counted as new rows
    # thus, these line returns are filtered out and so the actual number of operations is 10, not 30
    # df.reset_index(
    #     inplace=True, 
    #     drop=True
    # )

    return df

def read_inbetween_pages(pdf_file, table_areas_inbetween_pages, column_positions, number_of_pages):

    # create an empty DF
    in_between_pages_df = pd.DataFrame()

    # for i in range(2, number_of_pages):
    table = camelot.read_pdf(
        # define the encoding to utf-8, to manage characters such as 'é' or 'è' or 'à'
        encoding = 'utf-8',
        # filepath parameter
        filepath = pdf_file,
        # pages parameter, with a focus inbetween pages (not first, not last)
        pages = '2 - ' + str(number_of_pages),
        # areas parameter : list with coordinates, start by x1 / y1, then x2 / y2 /// here dimensions of page 1 applied
        table_areas = table_areas_inbetween_pages,
        # columns parameter : to be checked in the documentation how units (expressed in points) should be calculated
        columns = column_positions,
        # stream or lattice : two possibilities, in this case stream is relevant
        # --> clarify stream vs lattice differences
        flavor = 'stream'
    )

    # each generated table is concatenated to an inbetween pages dataframe
    for i in range (0, len(table) - 1):
        df = table[i].df
        # i starts at 0
        # 1st page starts at 1
        # so for inbetween pages (from second page on up to last page, excluded), file_page must be (i + 2)
        df.loc[:, "file_page"] = i + 2
        in_between_pages_df = pd.concat([in_between_pages_df, df])
    
    return in_between_pages_df

def read_last_page(pdf_file, table_areas_last_page, column_positions, number_of_pages):

    # output will be a table list and first page will have index 0
    
    table = camelot.read_pdf(
        # define the encoding to utf-8, to manage characters such as 'é' or 'è' or 'à' typical in the French language
        encoding = 'utf-8',
        # filepath parameter
        filepath = pdf_file,
        # pages parameter, with a focus on last page only
        pages = str(number_of_pages),
        # areas parameter : list with coordinates, start by x1 / y1, then x2 / y2 /// here dimensions of page 1 applied
        table_areas = table_areas_last_page,
        # columns parameter : to be checked in the documentation how units (expressed in points) should be calculated
        columns = column_positions,
        # stream or lattice : two possibilities, in this case stream is relevant
        # --> clarify stream vs lattice differences
        flavor = 'stream'
    )

    last_page_df = table[0].df
    last_page_df.loc[:, "file_page"] = number_of_pages

    return last_page_df

def add_metadata(df, file_name, extract_date, account_number):

        # file name as column
    df.loc[:, "file_name"] = file_name

    # extract date (YYYYMM)
    df.loc[:, "extract_date"] = extract_date

    # extract date (YYYYMM)
    df.loc[:, "account_number"] = account_number

    return df