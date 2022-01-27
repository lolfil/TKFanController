import clr  # pythonnet
import time
import serial


openhardwaremonitor_sensortypes = ['Voltage', 'Clock', 'Temperature', 'Load', 'Fan', 'Flow', 'Control', 'Level',
                                   'Factor', 'Power', 'Data', 'SmallData']
# duty low 27 high 255
# min 50-55 max 80
temps = [0.0, 0.0]
minPWM = 27
maxPWM = 255
minTemp = 50
maxTemp = 80
delta = maxTemp-minTemp
step = 255/delta
print(255/delta)


def get_pwm_width(t):
    # res =  min(minPWM + (t - minTemp) * step, 255)
    return max(min(min(minPWM + (t - minTemp) * step, 255), maxPWM), minPWM)


def min_to_max():
    for i in range(85, 90, 5):
        ser.write(bytes(str(i) + '\n', 'utf-8'))
        print(str(i))
        time.sleep(5)

    for i in range(255, 30, -5):
        ser.write(bytes(str(i) + '\n', 'utf-8'))
        print(str(i))
        time.sleep(0.5)


def initialize_openhardwaremonitor():
    file = 'OpenHardwareMonitorLib'
    clr.AddReference(file)

    from OpenHardwareMonitor import Hardware

    handle = Hardware.Computer()
    handle.MainboardEnabled = True
    handle.GPUEnabled = True
    handle.Open()
    return handle


def fetch_stats(handle):
    for i in handle.Hardware:
        i.Update()
        for sensor in i.Sensors:
            parse_sensor(sensor)
        for j in i.SubHardware:
            j.Update()
            for subsensor in j.Sensors:
                parse_sensor(subsensor)


def parse_sensor(sensor):
    if sensor.Value is not None:
        if type(sensor).__module__ == 'OpenHardwareMonitor.Hardware':
            sensortypes = openhardwaremonitor_sensortypes
        else:
            return

        if sensor.SensorType == sensortypes.index('Temperature'):
            # use the following code to detect CPU and GPU sensors
            # print("%s - %s - %s\u00B0C" % (sensor.Name, sensor.Identifier, sensor.Value))
            if str(sensor.Identifier) == "/lpc/it8688e/temperature/2":
                temps[0] = float(sensor.Value)
            if str(sensor.Identifier) == "/atigpu/0/temperature/0":
                temps[1] = float(sensor.Value)


if __name__ == "__main__":
    ser = serial.Serial('COM256', 9600)
    time.sleep(2)
    try:
        while True:
            HardwareHandle = initialize_openhardwaremonitor()
            fetch_stats(HardwareHandle)
            print("CPU temp is " + str(temps[0]))
            print("GPU temp is " + str(temps[1]))
            temp = max(temps[0], temps[1])
            pwm_width = get_pwm_width(temp)
            ser.write(bytes(str(pwm_width) + '\n', 'utf-8'))
            print("Temp is: %i\u00B0C --- PWM signal width is: %i/%i" % (temp, pwm_width, maxPWM))
            time.sleep(1)
    except KeyboardInterrupt:
        pass
