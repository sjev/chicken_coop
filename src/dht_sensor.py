import machine
import dht


class Sensor:
    def __init__(self,pin):
        self.sensor = dht.DHT22(machine.Pin(pin))
        self.data = None

    def measure(self):
        try:
            self.sensor.measure()
            data = {"Temperature":self.sensor.temperature(),"Humidity":self.sensor.humidity()}
        except Exception as e:
            data = {"Temperature":0,"Humidity":0}
            print('Could not read DHT sensor: %r' % e)

        self.data = data
        return data

if __name__ == "__main__":
    sensor = Sensor(13)
