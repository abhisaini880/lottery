""" Service to filter the regions data """

# Import dependencies
import pandas as pd
import os


def main(master_file_path, lastest_session_path):

    master_df = pd.read_excel(master_file_path)

    region_list = master_df["Lucky Draw Cluster"].unique().tolist()

    for region in region_list:
        os.mkdir(os.path.join(lastest_session_path, region))
        region_path = os.path.join(
            lastest_session_path, region, "participants.csv"
        )
        master_df[master_df["Lucky Draw Cluster"] == region].to_csv(
            region_path
        )

    return region_list


if __name__ == "__main__":
    pass
