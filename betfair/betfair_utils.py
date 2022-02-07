import logging

import betfairlightweight
import os

HOME = os.getenv("HOME")

"""
Historic is the API endpoint that can be used to
download data betfair provide.
https://historicdata.betfair.com/#/apidocs
"""

# setup logging
logging.basicConfig(level=logging.INFO)  # change to DEBUG to see log all updates

# create trading instance
trading = betfairlightweight.APIClient("adiga23@gmail.com", "Aar@07122014", app_key="gTjbUG3i87ZDyCw8",certs=f'{HOME}/betfair_keys')

# login
trading.login()

# get my data
my_data = trading.historic.get_my_data()
for i in my_data:
    print(i)


# get collection options (allows filtering)
collection_options = trading.historic.get_collection_options(
    "Tennis", "Basic Plan", 1, 3, 2017, 1, 3, 2017
)
print(collection_options)

# get advance basket data size
basket_size = trading.historic.get_data_size(
    "Horse Racing", "Basic Plan", 1, 3, 2017, 1, 3, 2017
)
print(basket_size)

# get file list

file_list = trading.historic.get_file_list(
    "Tennis",
    "Basic Plan",
    from_day=1,
    from_month=3,
    from_year=2017,
    to_day=1,
    to_month=3,
    to_year=2017,
    market_types_collection=[],
    countries_collection=[],
    file_type_collection=[],
)

print(file_list[0])
print(file_list[1])
print(len(file_list))

#download = trading.historic.download_file(file_path=file_list[0])
#print(download)
#exit()

# download the files
for count,file in enumerate(file_list):
    print(file)
    download = trading.historic.download_file(file_path=file)
    print(download)
    #if count == 2:
    #  break
