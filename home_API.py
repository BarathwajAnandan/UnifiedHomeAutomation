import aiohttp
import pysmartthings
import re
import os

def get_env(var):
    api_key = os.environ.get(var)
    return api_key
class SmartThings:

    def __init__(self):
        self.token = get_env('ST_API_KEY')
        self.test = None

    async def st_initiate(self):
        session = aiohttp.ClientSession()
        api = pysmartthings.SmartThings(session, self.token)
        initial_devices = await api.devices()

        self.st_devices = STDevices(initial_devices)

        


class STDevices:
    def __init__(self,args):
        self.all_devices = []
        for arg in args:
            arg_name = arg.label.lower()
            # arg_name = re.sub(r'', arg.label)
            self.all_devices.append(arg_name)
            setattr(self,arg_name,arg)
        print("SmartThings Devices:", self.all_devices)
    def get_all(self):
        return self.all_devices
    
  
async def refresh(device):
    res = device.status.refresh()
    await res



import requests
import json

from dataclasses import dataclass

class Devices:
    def __init__(self, args):
        for arg,v in args.items():
            setattr(self, arg, v)

class cmd:
    def __init__(self, args,properties):
        
        
        for arg in args:
            if arg == 'turn':
                if arg in properties:
                    arg_properties = properties[arg]
                else:
                    arg_properties = None
                setattr(self, arg, device_prop.turn(arg_properties))
            elif arg == 'brightness':
                if arg in properties:
                    arg_properties = properties[arg]
                else:
                    arg_properties = None
                setattr(self, arg, device_prop.brightness(arg_properties))
            elif arg == 'colorTem':
                if arg in properties:
                    arg_properties = properties[arg]
                else:
                    arg_properties = None
                setattr(self, arg, device_prop.temp(arg_properties))
            elif arg == 'color':
                if arg in properties:
                    arg_properties = properties[arg]
                else:
                    arg_properties = None
                setattr(self, arg, 0)

@dataclass
class DeviceInfo:
    device: str = None
    model: str = None
    deviceName: str = None
    controllable: bool = None
    properties: list = None
    retrievable: bool = None
    # supportCmds: = c
    def populate_cmds(self,args):
        self.cmds = cmd(args,self.properties)


@dataclass
class device_prop:

    def __str__(self):
        return 'device_prop'
    @dataclass
    class turn:
        properties: dict = None
        on: str = 'on'
        off: str = 'off'
        value: str = 'on'
        def __call__(self,new_value):
            self.set_value(new_value)
    
        def get_value(self):
            return self.value
        def string(self):
            return 'turn'
        def set_value(self,value:str):
            # print(value)
            assert value == 'on' or value == 'off', 'value can only be "on" or "off" '
            self.value = value
        def print_prop(self):
            print(self.properties)
        def __str__(self):
            return 'turn'
        def string(self):
            return 'turn'
            

    @dataclass
    class brightness:
        properties: dict = None
        min:int = 0
        max:int = 100
        _value: int = 20

        def __call__(self,new_value):
            self.set_value(new_value)

        def print_prop(self):
            print(self.properties)
        def set_value(self, new_value):
            assert new_value <=self.max, f" {new_value} out of bounds [{self.min},{self.max}]"
            assert new_value >=self.min
            self._value = new_value
        def get_value(self):
            return self._value
        def __str__(self):
            return 'brightness'

    @dataclass 
    class color:
        pass

    class temp:
        def __init__(self,properties):
            self.properties: dict = None
            self.value: int = 5000
            try:
                self.min = properties['range']['min']
            except:
                self.min = 3000
            try:
                self.max = properties['range']['max']
            except:
                self.max = 5000

        def set_value(self, new_value):
            if new_value < self.min or new_value > self.max:
                assert False, f" {new_value} out of bounds [{self.min},{self.max}]"
            self.value = new_value
        def get_value(self):
            return self.value
        def __str__():
            return 'colorTemp'

class Govee:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Govee, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    def __init__(self):
        self.base_url = 'https://developer-api.govee.com'
        self.api_key = get_env('GOVEE_API_KEY')
        self.default_header = {'Govee-API-Key': self.api_key}
        self.session = requests.Session()
        self.session.headers.update(self.default_header)
        self.devices_raw = None
        # self.models = self.get_model_names()
        self.deviceNames = self.get_deviceNames()
        self.content_header = {'Govee-API-Key': self.api_key, 'Content-Type' : 'application/json' }
        self.initiate()
    def initiate(self):
        if self.devices_raw == None:
            self.get_devices()
        self.populate_devices()
        
    def update_header(self, type = 'default'):
        if type == 'default':
            curr_header = self.default_header
        if type == 'content':
            curr_header = self.content_header

        self.session.headers.update(curr_header)
    def get(self, endpoint='',params = None):
        url = f"{self.base_url}/{endpoint}"
        response = self.session.get(url,params = params)
        return response.json()
    
    def put(self, endpoint='',params = None):
        url = f"{self.base_url}/{endpoint}"
        response = self.session.put(url,params = params)
        return response
    
    def update_devices(self):
        self.devices_raw = self.get('v1/devices')
        

    def get_devices(self):
        if self.devices_raw == None:
            self.update_devices()

        # return self.devices_raw
    
    def supported_cmds(self,model):
        return self.get_model_attribute(model, 'supportCmds')

    def get_attributes_list(self, model):
        for i in self.devices_raw['data']['devices']:
            if i['model'] == model:
                return i.keys()
        return []
    
    def get_deviceNames(self):
  
        temp_deviceNames = []
        if self.devices_raw  == None:
            self.update_devices()
        for i in self.devices_raw['data']['devices']:
            temp_deviceNames.append(i['deviceName'])
        print("Available devices:", temp_deviceNames)
        return temp_deviceNames

    def get_device_states(self,name):
        self.update_header(type = 'content')
        response = self.get('v1/devices/state?',params={'device':self.devices_dict[name].device, 'model': self.devices_dict[name].model})
        return response
    
    def populate_devices(self): 
        if self.devices_raw == None:
            self.update_devices()

        self.devices_dict = {}
        keys = ['device','model','deviceName','controllable','properties','retrievable' ]
        for item in self.devices_raw['data']['devices']:
            # item = self.devices_raw['data']['devices'][i]
            dev_values = []
            for k in keys:
                v = item[k]
                dev_values.append(v)
            temp_info = DeviceInfo(*dev_values)
            temp_info.populate_cmds(item['supportCmds'])
            dev_name_lower = item['deviceName'].lower()
            self.devices_dict[item['deviceName']] = temp_info
        self.devices = Devices(self.devices_dict)
        

    def get_model_attribute(self, model, attribute):
        for i in self.devices_raw['data']['devices']:
            if i['model'] == model:
                return i.get(attribute)
        return None
        

    def control_govee_device(self,device, model, command, value):
        url = f'{self.base_url}/v1/devices/control'
        self.update_header('content')
        body = {
            'device': device,
            'model': model,
            'cmd': {
                'name': command,
                'value': value
            }
        }
    
    def control_device_by_name(self,name, command, value):
        url = f'{self.base_url}/v1/devices/control'
        self.update_header('content')
        device, model = self.devices_dict[name].device, self.devices_dict[name].model
        body = {
            'device': device,
            'model': model,
            'cmd': {
                'name': command,
                'value': value
            }
        }

        response = requests.put(url, headers=self.content_header, data=json.dumps(body))
        return response.json()
    
    def control(self,name, _command):
        url = f'{self.base_url}/v1/devices/control'
        self.update_header('content')
        device, model = self.devices_dict[name].device, self.devices_dict[name].model
        cmd_name = _command.__class__.__name__
        cmd_value = _command.get_value()

        body = {
            'device': device,
            'model': model,
            'cmd': {
                'name': cmd_name,
                'value': cmd_value
            }
        }
        print(body)

        response = requests.put(url, headers=self.content_header, data=json.dumps(body))
        return response.json()
    
class Home(Govee,SmartThings):
    def __init__(self):
        SmartThings.__init__(self)
        Govee.__init__(self)

    async def __call__(self,device_name,device_cmd):
        if hasattr(self.st_devices, device_name):
            # print("ST")
            device = getattr(self.st_devices, device_name)
            # print(type(device))
            if device_cmd == 'turn_on':
                await device.switch_on()
            elif device_cmd == 'turn_off':
                await device.switch_off()

        if hasattr(self.devices, device_name):
            print("Govee!")
            device = getattr(self.devices, device_name)
            print(type(device))
            if device_cmd == 'turn_on':
                device.cmds.turn.set_value('on') 
                self.control(device_name, device.cmds.turn)
            elif  device_cmd == 'turn_off':
                device.cmds.turn.set_value('off')
                self.control(device_name, device.cmds.turn)
            else:
                print("Govee : poda punda. Implement Pannu modhalla!")

    
# govee = Govee()
# govee.initiate()
