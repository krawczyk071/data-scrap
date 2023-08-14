def extract_oferta_from_json(jsondata):

    def is_oferta(jsondata):
        body = jsondata['props']['pageProps']
        if 'ad' in body.keys():
            return True
        else:
            return False

    def is_lift():
        try:
            return [x['values'][0].replace(':',"") for x in ad['additionalInformation'] if x['label']=='lift'][0]
        except:
            return 'n'
        
    chk_is_oferta = is_oferta(jsondata)

    body=jsondata['props']['pageProps']

    info = {'userSessionId':body['userSessionId'],'isBotDetected':body['isBotDetected']}

    if not chk_is_oferta:
        return {'is_oferta':chk_is_oferta,'info':info,'data':None}

    ad = body['ad']

    main={'id':ad['id'],
    'publicId':ad['publicId'],
    'advertType':ad['advertType'],
    'createdAt':ad['createdAt'],
    'modifiedAt':ad['modifiedAt'],
    'description':ad['description'],
    'exclusiveOffer':ad['exclusiveOffer'],
    'externalId':ad['externalId'],
    'features':','.join(ad['features']),
    'title':ad['title'],
    'agency':ad['agency']['name'] if ad['agency'] else '',
    'adCategoryname':ad['adCategory']['name'],
    'adCategorytype':ad['adCategory']['type'],
    'latitude':ad['location']['coordinates'].get('latitude'),
    'longitude':ad['location']['coordinates'].get('longitude'),
    'cityname':ad['location']['address']['city']['name'] if ad['location']['address']['city'] else '',
    'districtname':ad['location']['address']['district']['name'] if ad['location']['address']['district'] else '',
    'streetname':ad['location']['address']['street']['name'] if ad['location']['address']['street'] else '',
    'number':ad['location']['address']['street']['number'] if ad['location']['address']['street'] else '',
    'rent':ad['property']['rent']['value'] if ((ad.get('property'))and(ad['property'].get('rent'))) else '',
    'costs':','.join(ad['property']['costs']) if ((ad.get('property'))and(ad['property'].get('costs'))) else '',
    'condition':ad['property']['condition'] if ((ad.get('property'))and(ad['property'].get('condition'))) else '',
    'ownership':ad['property']['ownership'] if ((ad.get('property'))and(ad['property'].get('ownership'))) else '',
    'ownername':ad['owner']['name'],
    'phones':','.join(ad['owner']['phones']),
    'images':','.join([x['medium'] for x in ad['images']]),
    'Area':ad['target']['Area'],
    'Building_floors_num':ad['target']['Building_floors_num'] if ad['target'].get('Building_floors_num') else '',
    'Building_type':','.join(ad['target']['Building_type']) if ad['target'].get('Building_type') else '',
    'Building_material':','.join(ad['target']['Building_material']) if ad['target'].get('Building_material') else '',
    'Build_year':ad['target']['Build_year'] if ad['target'].get('Build_year') else '',
    'Construction_status':','.join(ad['target']['Construction_status']) if ad['target'].get('Construction_status') else '',
    'Extras_types':','.join(ad['target']['Extras_types']) if ad['target'].get('Extras_types') else '',
    'Floor_no':','.join(ad['target']['Floor_no']) if ad['target'].get('Floor_no') else '',
    'Heating':','.join(ad['target']['Heating']) if ad['target'].get('Heating') else '',
    'MarketType':ad['target']['MarketType'],
    'OfferType':ad['target']['OfferType'],
    'Price':ad['target']['Price'] if ad['target'].get('Price') else '',
    'ProperType':ad['target']['ProperType'],
    'Rooms_num':','.join(ad['target']['Rooms_num']) if ad['target'].get('Rooms_num') else '',
    'Windows_type':','.join(ad['target']['Windows_type']) if ad['target'].get('Windows_type') else '',
    'Lift':is_lift()}

    if ad['location'].get('reverseGeocoding'):
        geo={k:v for k,v in [(x['locationLevel'],x['name']) for x in ad['location']['reverseGeocoding']['locations']]}
        main.update(geo)

    return {'is_oferta':chk_is_oferta,'info':info,'data':main}

def extract_ads_from_json(jsondata):

    body=jsondata['props']['pageProps']
    ads = body['data']['searchAds']

    info = {'userSessionId':body['userSessionId'],'isBotDetected':body['isBotDetected']}
    pagination={
        'totalResults':ads['pagination']['totalResults'], 
        'itemsPerPage':ads['pagination']['itemsPerPage'], 
        'page':ads['pagination']['page'], 
        'totalPages':ads['pagination']['totalPages']}

    data_list =[]
    for item in ads['items']:

        main={'id':item['id'],
            'title':item['title'],
            'slug':item['slug'],
            'estate':item['estate'],
            'developmentId':item['developmentId'],
            'transaction':item['transaction'],
            'isPrivateOwner':item['isPrivateOwner'],
            'agency':item['agency']['name'] if item.get('agency') else '',
            'totalPrice':item['totalPrice']['value'] if item.get('totalPrice') else '',
            'rentPrice':item['rentPrice']['value'] if item.get('rentPrice') else '',
            'areaInSquareMeters':item['areaInSquareMeters'],
            'roomsNumber':item['roomsNumber'],
            'peoplePerRoom':item['peoplePerRoom'],
            'dateCreated':item['dateCreated'],
            'dateCreatedFirst':item['dateCreatedFirst'],
            'pushedUpAt':item['pushedUpAt'], 

            'latitude':item['location']['coordinates'].get('latitude') if item['location'].get('coordinates') else '',
            'longitude':item['location']['coordinates'].get('longitude') if item['location'].get('coordinates') else '',
            'cityname':item['location']['address']['city']['name'] if item['location']['address']['city'] else '',
            'districtname':item['location']['address']['district']['name'] if item['location']['address'].get('district') else '',
            'streetname':item['location']['address']['street']['name'] if item['location']['address']['street'] else '',
            'number':item['location']['address']['street']['number'] if item['location']['address']['street'] else '',
            'geo':item['location']['reverseGeocoding']['locations'][-1]['fullName'] if item['location']['reverseGeocoding'].get('locations') else '',
        }
        
        data_list.append(main)

    return {'pagination':pagination,'info':info,'data_list':data_list}