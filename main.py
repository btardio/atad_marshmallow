

import requests
import json
import pprint

DEVMODE = True

responsestr = ''

# if we are in development mode read from a text file so we don't get throttled
if not DEVMODE:
    queryurl = 'http://api.citybik.es/v2/networks/cyclopolis-rhodes'
    response = requests.get(queryurl) # make the get request
    responsestr = response.text # the response
else:
    with open('response.txt', 'r') as response: # open the file for reading
        responsestr = response.read() # read the file
        


# note: class member variable names must be names corresponding to the 
#       dictionary keys
def method00():
    
    from marshmallow import ( Schema, fields, pprint as mpprint )

    # Marshmallow requires a schema based on the json string we receive
    # from the API. To get a better understanding of how the schema is to
    # be created we can print the json string indented
    #
    # print (json.dumps(json.loads(responsestr), sort_keys=True, indent=4))
    #
    # what we see is a structure that is nested, for each level of nesting
    # we create a class
    # the class members are classes of marshmallow.fields, there are other
    # options to use, include Decimal and DataTime, full documentation is
    # available on the marshmallow site
    #
    # note: class member variable names must be names corresponding to the 
    #       dictionary keys

    class ExtraSchema(Schema):
        slots = fields.Integer()
    
    class LocationSchema(Schema):
        city = fields.String()
        country = fields.String()
        latitude = fields.String()
        longitude = fields.String()
        
    class StationSchema(Schema):
        empty_slots = fields.Integer()
        # for classes that have nested subclasses we use fields.Nested
        extra = fields.Nested(ExtraSchema)
        # if this field is missing then an error will be thrown after loading
        free_bikes = fields.Integer(required=True)
        id = fields.String()
        latitude = fields.Float()
        longitude = fields.Float()
        name = fields.String(required=True)
        # b/c Object of type datetime is not JSON serializable, we choose String
        timestamp = fields.String()
    
    class NetworkSchema(Schema):
        company = fields.List(fields.String())
        href = fields.String()
        id = fields.String()
        location = fields.Nested(LocationSchema, required=True)
        name = fields.String()
        # for classes that have lists we use fields.List
        stations = fields.List(fields.Nested(StationSchema))
        
    class CityBikesAPISchema(Schema):
        network = fields.Nested(NetworkSchema, required=True)
    
    # instantiate the schema
    # we can specify that we only want to load certain items. Items on the same
    # and higher levels of nesting will also be loaded
    schema = CityBikesAPISchema(only=['network.stations.name', 
                                      'network.stations.free_bikes'])
    
    # load the schema, creating our result
    result = schema.loads(responsestr)
    
    # check for errors
    if len(result.errors.keys()) == 0: pass
    else: raise Exception(str(result.errors))
    
    # finally print out the results
    # note: unfortunately our result.data is a dict, in the next section the
    # dict result is converted to a class
    for station in result.data['network']['stations']:
        print(station['name'] + ' | Free Bikes: ' + str(station['free_bikes']))
    

# this method improves on the previous method by making a class instance
# instead of using nested dictionaries

def method01():
    
    from marshmallow import ( Schema, fields, pprint as mpprint, 
                              post_load as mpost_load )



    # the classes created here are similar to the classes created in the
    # previous example except they don't involve marshmallow. These
    # classes have an __init__ method which assigns class member variables
    # and the argument names of the __init__ method are identical to the
    # variable names in the previous example and identical to the keys returned
    # by the api. The repr function is just a simple helper for printing 
    # the classes in a way that helps us to debug.
    class Extra:
        def __init__(self, slots):
            self.slots = slots
            
        def __repr__(self):
            return str(self.__class__) + " " + str(self.__dict__)

    class Location:
        def __init__(self, city, country):
            self.city = city
            self.country = country
            
        def __repr__(self):
            return str(self.__class__) + " " + str(self.__dict__)
        
    class Station:
        def __init__(self, empty_slots, extra, free_bikes, id, latitude, 
                     longitude, name, timestamp):
            self.empty_slots = empty_slots
            self.extra = extra
            self.free_bikes = free_bikes
            self.id = id
            self.latitude = latitude
            self.longitude = longitude
            self.name = name
            self.timestamp = timestamp
            
        def __repr__(self):
            return str(self.__class__) + " " + str(self.__dict__)
            
    class Network:
        def __init__(self, company, href, id, location, name, stations):
            self.company = company
            self.href = href
            self.id = id
            self.location = location # class
            self.name = name
            self.stations = stations # list
            
        def __repr__(self):
            return str(self.__class__) + " " + str(self.__dict__)

    class CityBikesAPI:
        def __init__(self, network):
            
            self.network = network
            #self.network = Network(adict['network']['companies'])
            
        def __repr__(self):
            return str(self.__class__) + " " + str(self.__dict__)

    # the next section contains the same schema's that we have defined above
    # we have added an @post_load decorator function which will be executed
    # after the schema is loaded
    #
    # note: returning serializable objects from @post_load will allow us
    # to serialize / deserialize our class object into json easier
    #
    # our post load function instantiates a class using the dictionary converted
    # to function arguments.
    # what ** does is specify that we would like Python to look at the dict 
    # as an argument list, instead of a dictionary, this means that the list of 
    # arguments would be, for example:
    # city='Rhodes', country='GR', id='cyclopolis-rhodes' etc., 
    # in JavaScript this would be similar to ...
    # note: # argument lists are dictionaries in their own right but we
    # are specifying how Python should interpret them
    
    class ExtraSchema(Schema):
        slots = fields.Integer()
        
        @mpost_load
        def postload(self, data): return Extra(**data)
    
    class LocationSchema(Schema):
        city = fields.String()
        country = fields.String()
        
        @mpost_load
        def postload(self, data): return Location(**data)
        
    class StationSchema(Schema):
        empty_slots = fields.Integer()
        extra = fields.Nested(ExtraSchema)
        free_bikes = fields.Integer(required=True)
        id = fields.String()
        latitude = fields.Float()
        longitude = fields.Float()
        name = fields.String(required=True)
        timestamp = fields.String() # b/c Object of type datetime is not JSON serializable
        
        @mpost_load
        def postload(self, data): return Station(**data)
    
    class NetworkSchema(Schema):
        company = fields.List(fields.String())
        href = fields.String()
        id = fields.String()
        location = fields.Nested(LocationSchema, required=True)
        name = fields.String()
        stations = fields.List(fields.Nested(StationSchema), required=True)
        
        @mpost_load
        def postload(self, data): return Network(**data)
        
    class CityBikesAPISchema(Schema):

        @mpost_load
        def postload(self, data):
             
            return CityBikesAPI(**data)

        network = fields.Nested(NetworkSchema, required=True)

    schema = CityBikesAPISchema()

    result = schema.loads(responsestr, partial=False)

    if len(result.errors.keys()) == 0: pass
    else: raise Exception(str(result.errors))

    print ( result.data )
    
    out = schema.dumps(result.data)
    
    print(out.data)
    
    
    # to illustrate the benefit of this, say there are two urls, one url
    # for reading and one url for writing, to change the name of the company
    # you would need:
    
    datain = schema.loads(responsestr, partial=False)
    
    if len(result.errors.keys()) == 0: pass
    else: raise Exception(str(result.errors))

    result.data.network.company = ['Systems Cyclopolis']
    
    dataout = schema.dumps(datain.data)
    
    print(dataout)
    
# method02 uses SimpleNamespace
# note: this is not json serializable
def method02():
    from types import SimpleNamespace

    # 
    # object_hook is passed a lambda function that expects the normal
    # return from json.loads, a dictionary, for each nested dictionary
    # it will call the lambda function
    #
    # the lambda function returns SimpleNamespace(**arglist)
    #
    # what **arglist does to our arglist is specify that we would like
    # Python to look at arglist as an argument list, instead of a dictionary
    # this means that the list of arguments is city='Rhodes', country='GR', 
    # id='cyclopolis-rhodes' etc., in JavaScript this would be similar to ...
    # note: # argument lists are dictionaries in their own right but we
    # are specifying how Python should interpret them
    # 
    # the SimpleNamespace function creates a class object from these 
    # argument lists which is then returned
    #
    # if you are interested in what SimpleNamespace does you kind find
    # more information here: 
    # https://docs.python.org/3/library/types.html?highlight=types#additional-utility-classes-and-functions
    #
    # if this makes little sense to you read on because this technique is
    # better summarized using the Marshmallow package
    #
    # an interesting task to discover how Python interprets ** is discovering
    # what is printed with:
    # print(dict(**json.loads(responsestr)))
    # print(json.loads(responsestr))
    # and understanding why it's an error to print:
    # print(**json.loads(responsestr))
    
    boundclass = json.loads(responsestr, object_hook=lambda arglist: SimpleNamespace(**arglist))
    
    for station in boundclass.network.stations:
        print(station.name + ' | Free Bikes: ' + str(station.free_bikes))
    
    print('type(boundclass.network.stations): ' + str(type(boundclass.network.stations)))


# this method is preferred method, however it takes a little bit of extra code
# this method combined with method02 is best
def method03():
    
    class Station(object):
        # constructor for station, simply assigns the class member variable
        # name and free_bikes
        def __init__(self, name, free_bikes):
            self.name = name
            self.free_bikes = free_bikes
        # string operator/built-in, python calls these magic objects/attributes
        def __str__(self):
            return str(self.name) + ' | Free Bikes: ' + str(self.free_bikes)

    # this object_decoder receives the dictionaries that are part of the json
    # obj recursively, each dictionary can be determined by looking at the keys
    def object_decoder(obj):
        # determine if the 'free_bikes' key and 'name' key is in the dictionary
        # this let's us know that this part of the information received from
        # the api is relevant and we want to turn it into a class
        if 'free_bikes' in obj and 'name' in obj:
            # instantiate a class from the stations and return the class instead
            # of returning a dictionary with unneeded information
            return Station(obj['name'], obj['free_bikes'])
        
        # for all other dictionaries in the list, don't decode them into a class
        # but return them so that we can keep the structure of the json object
        return obj
    
    def object_decode(str):
        
        # for every dict in the json str recursively call object_decoder
        obj = json.loads(str, object_hook=object_decoder)
        
        if ( 'network' in obj and 'stations' in obj['network'] ):
            # because we don't need the other parts of the information returned 
            # from the API we can only return the ['network']['stations'] part
            # which will be a list of the classes we instantiated
            # return only the stations
            
            return obj['network']['stations']
        else:
            # this could alternatively raise an error which would indicate
            # that the information returned to us from the API is not what we
            # expected
            return None

    # start the object_decode process
    boundclasslist = object_decode(responsestr)

    # print the items in the list
    for item in boundclasslist:
        print(item)
    
    # print the type of the list
    print('type(boundclasslist): ' + str(type(boundclasslist)))
    
    
    
    
    
method00()
method01()
method02()
