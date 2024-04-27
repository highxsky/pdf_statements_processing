import config as cfg # root folder + tables and columns measurements
import functions as fn # functions used in the script
import pandas as pd

if __name__ == "__main__":

    # loop over each file in root folder

    # get files metadata (file name: [file_path, extract_date, account_number, number_of_pages])
    dict = fn.get_files_metadata(cfg.root_dir)

    # empty dataframe for concatenation
    global_df = pd.DataFrame()

    for key, value in dict.items():
        file_path = value[0]
        extraction_date = value[1]
        account_number = value[2]
        number_of_pages = value[3]

        # reading first page data
        first_page_df = fn.read_first_page(
            file_path, 
            cfg.table_areas_first_page, 
            cfg.column_positions
        )

        # reading "inbetween" pages data
        inbetween_pages_df = fn.read_inbetween_pages(
            file_path, 
            cfg.table_areas_inbetween_pages, 
            cfg.column_positions, 
            number_of_pages
        )

        # reading last page data
        last_page_df = fn.read_last_page(
            file_path, 
            cfg.table_areas_last_page, 
            cfg.column_positions, 
            number_of_pages
        )

        # creating a list of dataframes
        all_pages_dfs = [first_page_df, inbetween_pages_df, last_page_df]
            
        # cleaning each dataframe in the list
        # and concatenating these into a single one
        all_pages_cleaned_df = pd.concat(
            [fn.clean_dataframe(df) for df in all_pages_dfs],
            ignore_index=True
        )

        # adding meta data to the dataframe
        all_pages_cleaned_df = fn.add_metadata(all_pages_cleaned_df, key, extraction_date, account_number)

        # concatenating each 
        global_df = pd.concat(
            [global_df, all_pages_cleaned_df],
            ignore_index=True
        )

        global_df.to_excel(cfg.output_path)