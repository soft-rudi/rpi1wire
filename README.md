# Raspberry Pi 1-Wire plugin

# Requirements

This plugin has been developed for the Raspberry Pi. It allows easy access to 1-Wire - sensors.
We tested the plugin with the Raspberry Pi B and the temperature sensor DS18B20.

## Supported Hardware

Tested width:
Raspberry Pi Model B
1-Wire - Sensor DS18B20

# Configuration

## plugin.conf

<pre>
[rpi1wire]
   class_name = Rpi1Wire
   class_path = plugins.rpi1wire
#   dirname = "/sys/bus/w1/devices"
#   cycle = 120
</pre>

dirname
    is the path where the Raspberry provides the values of the 1-wire - sensors
    default "/sys/bus/w1/devices"

cycle
    is the period in which the values are updated
    default 120 seconds

## items.conf

[rpi1wire]
    [[sensor_list]]
        name = Sensor-List
        type = str
        visu_acl = ro
    [[sensors]]
        name = Sensors
        type = num
        visu_acl = ro

sh.rpi1wire.sensor_list()
    - contains a list of all found sensors

sh.rpi1wire.sensors()
    - contains the number of sensors found

### rpi1wire_name

The name of the 1-wire - sensor
    - rpi1wire_name or rpi1wire_id are possible

### rpi1wire_id

The id of the 1-wire - sensor
    - rpi1wire_name or rpi1wire_id are possible

### rpi1wire_update

If you trigger this item, the sensors are re-searched without restart the server


### Example


<pre>
# items/my.conf

[someroom]
    [[mytemperature]]
        name = my Name
        type = num
        visu_acl = ro
        rpi1wire_name = rpi_temp1
        rpi1wire_unit = Grad C
        sqlite = yes

or

[someroom]
    [[mytemperature]]
        name = my Name
        name = Wohnzimme Raumtemperatur
        type = num
        visu_acl = ro
        rpi1wire_id = 28-0215018970ff
        rpi1wire_unit = Grad C
        sqlite = yes

[rpi1wire]
    [[update]]
        name = Update Sensor-List
        type = bool
        visu_acl = rw
        rpi1wire_update = 1

</pre>

