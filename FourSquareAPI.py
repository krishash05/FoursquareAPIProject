import json
import requests
import csv
from matplotlib import pyplot as plt
import gmplot
import webbrowser

#my foursquare client id and client secret
my_client_id='VG454LSU3QC4VTUVSVF4NZAEP3R3CGAAALOMQZBDJXHVI2RP'
my_client_secret='5QXKJIBJM5EP2MESAX3U54HBCU20UMTPXNLDYXWOC3DTQ3LJ'

#searching the venue function
def searching_add(storage,No_limit):
    url = 'https://api.foursquare.com/v2/venues/explore' #url of api
    selected_location=storage #selected location by user
    coordinates=finding_ll(selected_location) #coordinates of the location, output of find_ll function
    my_coordinates='{},{}'.format(coordinates[0],coordinates[1]) #change the format of the coordinates to the acceptable format for api
    selected_query=input('What are you looking for? (eg. food/bar/coffee/nightlife/shopping)  ') #selected query
    params = dict( #make a dictionary of parameters
    client_id=my_client_id, #my_client ID
    client_secret=my_client_secret, #my client secret code
    v='20170801', #version of API
    ll=my_coordinates, #coordinates of selected location
    query=selected_query,
    limit=No_limit) #number of result that user want to see
    resp = requests.get(url=url, params=params) #get the results
    my_data = json.loads(resp.text) #load in json
    print()
    print('Total results: ',my_data['response']['totalResults']) #print the total number of venue that it found
    print()
    print('Top {} recommended venues for you:'.format(No_limit)) #print the recommended venues
    print('-----------------------------------')
    i=0
    d_id=dict() #dictionary for collecting IDs
    venue_names=[] #list of venue names
    venue_rating=[] #list of venue ratings
    for i in range(No_limit): #run a loop to get the venue ID, name, phone number, address, and rating
        try:
            ven_id=my_data['response']['groups'][0]['items'][i]['venue']['id']
            name=my_data['response']['groups'][0]['items'][i]['venue']['name']
            phone_number=my_data['response']['groups'][0]['items'][i]['venue']['contact']['phone']
            address=my_data['response']['groups'][0]['items'][i]['venue']['location']['formattedAddress']
            rating = my_data['response']['groups'][0]['items'][i]['venue']['rating']
            j=i+1 #add 1 to i to start the dictionary key from 1
            d_id[j] = ven_id #add IDs to the dictionary
            print('No.:',j)
            venue_names.append(name) #append the venue names to the list
            print('Venue name: ',name)
            print('Venue phone number: ',phone_number)
            str=""
            for item in address: #print the address in the correct form
                str=str+','+' '+item
            print('Venue address: ',str[1:])
            print('******************************************************************************************')
            venue_rating.append(rating)
        except KeyError:
            pass
        except IndexError:
            pass

    file = zip(venue_names,venue_rating) #zip the venue names and ratings for analysis
    #make a CSV file for the output including the location name and type of request in its name
    with open ('venue_{}_{}.csv'.format(selected_location,selected_query), 'w', newline='') as f:  # Just use 'w' mode in 3.x
        my_writer = csv.writer(f)
        my_writer.writerow ( ('Venue Name', 'Venue Rating') )
        for row in file:
            my_writer.writerow(row)
        print('venue_{}_{}.csv '.format(selected_location,selected_query),'is generated!')#print that the file is generated!

    print ()
    p = input (
        "Do you want to see the ratings of {}? (y/n)".format ( selected_query ) )  # ask user to plot the ratings
    p = p.lower ()  # make the input lower case to avoid errors of input
    if p == 'y':
        plotting ( venue_names, venue_rating, selected_location, selected_query )  # run the plotting function
    else:
        pass

    selector='' #to show more details about the venue
    while selector != 0:
        print()
        # to show more details about the venue, it asks for the venue no.
        selector=int(input('To get more details of a venue, '
                           'please input the No. corresponding to the venue (Type 0 to exit): '))

        if selector == 0:
            break
        else:
            venue_details (d_id[selector],selected_location)#run the venue details function to get more details


#venue detail function
def venue_details(storage,location):
    ven_id = storage #venue ID will be the input of function
    url = 'https://api.foursquare.com/v2/venues/{}'.format(ven_id) #URL of API

    params = dict( #dictionary of parameters
        client_id=my_client_id, #my_client ID
        client_secret=my_client_secret, #my_client secret code
        v='20170801') #version of API
    resp = requests.get(url=url, params=params) #send the get request
    my_data = json.loads(resp.text) #load in the JSON format
    v=my_data['response']['venue'] #make list of details about the venue
    try:
        if v:
            print('Venue Name: {}'.format(v['name'])) #print the name
            print ( 'Venue phone number: {}'.format(v['contact']['phone'])) #print Phone number
            address=v['location']['formattedAddress'] #save the address
            str = ""
            for item in address:#prepare the address with proper format
                str = str + ',' + ' ' + item

            print ('Venue address: {}'.format(str[1:]))
            print('Venue Rating: {}'.format(v['rating'])) #print the rating
            print ('Venue Pricing: {}'.format(v['price']['message'])) #print the price
            print ('Venue url: {}'.format(v['url'])) #print the url
            print ('Venue hours: {}'.format(v['hours']['status'])) #print the hours and status of venue
            show_map = input ( 'Do you want to see the location on Google Maps? (y/n)' )
            show_map = show_map.lower ()
            if show_map == 'y':
                location_coordinates = finding_ll (location)
                venue_coordinates = finding_ll (address)
                gmap = gmplot.GoogleMapPlotter ( location_coordinates[0], location_coordinates[1], 16 )
                lat = []
                lng = []
                for i in range ( 2 ):
                    lat.append ( venue_coordinates[0] )
                    lng.append ( venue_coordinates[1] )
                gmap.scatter ( lat, lng, '#3B0B39', size=100, marker=False )
                gmap.draw ( "map.html" )
                print ( 'The map generated!' )
                webbrowser.open_new_tab( 'map.html' )
            else:
                pass
    except KeyError:
        pass

#create a function to plot the ratings
def plotting(venue_names,venue_rating,selected_location,selected_query):
    num_venues=[] #make a list of venue names
    for i in range(len(venue_names)):
        num_venues.append(i) #make list of numbers based on length of the list
    plt.bar (num_venues,venue_rating, color="red" ) #create bar plot
    plt.title ( "Rating of top {} {} in {}".format(len(venue_names),selected_query,selected_location))
    plt.ylabel ("Rating")
    plt.xlabel ("Venue Number")
    print ()
    plt.show ()


#use google API and get the latitude and longitude of the input address
def finding_ll(city):
    address = city
    api_key= "AIzaSyAPcTWff3YR8OwZ7o79P95s3-OfeRx1i8c"
    response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address={0}&key={1}'.format(address, api_key))
    resp_json_payload = response.json()


    if resp_json_payload['status'] == 'OK':
        latitude = resp_json_payload['results'][0]['geometry']['location']['lat']
        longitude = resp_json_payload['results'][0]['geometry']['location']['lng']
        return latitude, longitude


def main():
    '''The main function of FourSquare API'''
    print()
    print('Welcome to FourSquare API ')
    selection = ''
    while selection != 'q':
        print()
        #The input can be the city or the exact address
        selection = input ( 'Which area do you want to explore? (Press q To exit)' )
        if selection == 'q':
            break
        else:
            No_limit = int ( input ( 'Number of venues: (e.g. 10)' ) )
            searching_add(selection,No_limit)  # process the request and run the function



if __name__ == "__main__":
    main()