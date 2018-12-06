# Data Binding in Python

For this tutorial I will be using the City Bikes API: <http://api.citybik.es/v2/>

Firstly, it is important to mention that all objects / classes in Python are implemented as dictionaries at a low level, so the processes mentioned in this tutorial may be viewed as a new organizational structure that creates additional dictionary functionality. Don't worry, it'll make more sense after reading this.

In this tutorial I will present 3 ways to accomplish the task of creating a Python class from a JSON string. We typically work with JSON as a dictionary, referencing variables using jsonobj['jsonentry']. This tutorial will enable us to reference variables using jsonobj.jsonentry and some methods will allow us further functionality on top of this.

I have come across data binding using TypeScript/Angular as well as Spring Boot. I am no expert in the subject matter but from my experience this has been used to add type checking, validation and encapsulation. This process also can be integrated with a database for persistent storage.

I will be using the Marshmallow package for this tutorial.

<https://marshmallow.readthedocs.io>

## Preparing an environment

```python

import requests
import json
import pprint

DEVMODE = True

responsestr = ''

# if we are in development mode, read from a text file so we don't get throttled
if not DEVMODE:
    queryurl = 'http://api.citybik.es/v2/networks/cyclopolis-rhodes'
    response = requests.get(queryurl) # make the get request
    responsestr = response.text # the response
else:
    with open('response.txt', 'r') as response: # open the file for reading
        responsestr = response.read() # read the file
        
```

## Using Marshmallow

```python
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
```    

## Method Extension


```python
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
```

## Shortest but least functional method

This method will create a namespace object which is not serializable but if you are only consuming data this could be this best solution.

```python
def method02():
    from types import SimpleNamespace
    
    boundclass = json.loads(responsestr, 
      object_hook=lambda arglist: SimpleNamespace(**arglist))
    
    for station in boundclass.network.stations:
        print(station.name + ' | Free Bikes: ' + str(station.free_bikes))
    
    print('type(boundclass.network.stations): ' + 
           str(type(boundclass.network.stations)))
```


# Conclusion

So we have seen marshmallow in practice, starting with a simple example that introduces the package. I want to add that marshmallow also allows us to add validation, partial loading, dump_only, load_only, filter and load decorators to our json dictionary objects.

The second method we have seen involved a short way to manipulate the data using class objects instead of dictionaries. This example showed us that we could easily load a json string, pass the class object to a function to change or alter the data and then dumps the resulting object to another API endpoint.

We could have additionally encapsulated the data in our classes with get and set methods, which is typically done in Java, but Python does not enforce encapsulation.

I hope this tutorial has shown you an organizational technique for working with JSON return strings. Please let feel free to send me an email with critique or constructive criticism.



