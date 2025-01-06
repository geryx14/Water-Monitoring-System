# IoT-Based Water Monitoring System

## Description
This project provides an affordable and efficient way to monitor water levels and quality using IoT technology. With real-time data transmission and cloud integration, it ensures better resource management.

## Key Features
- Real-time monitoring of water parameters
- Database integration for remote access
- Simple and scalable design
- to give saveral notifications alert to email and telegram

## Hardware Requirements
- ESP32 microcontroller
- Raspberry pi 4B
- ADS115 Analog Digital Converter
- Ultrasonic sensor (URM-09) : https://wiki.dfrobot.com/URM09_Ultrasonic_Sensor_(Gravity_Analog)_SKU_SEN0307
- Gravity: Analog Turbidity Sensor for Arduino LINK : https://www.dfrobot.com/product-1394.html?srsltid=AfmBOop4nN1BXaXB-rLAD9B4F6cB8y7F4hOIFvNodXXyrF563nFi_e-l
- Gravity: Analog pH Sensor / Meter Pro Kit for Arduino : https://www.dfrobot.com/product-1110.html
- DC PSU 5 Volt
- DC PSU 24 Volt
- Relay 5V DC
- Relay 3 fasa solidstate

## Required Libraries and Dependencies

To ensure the system works properly, install the following libraries and dependencies for ESP32, Raspberry Pi, and Node-RED.


### **ESP32 Libraries**
Ensure the following libraries are installed in the Arduino IDE or PlatformIO:

1. **WiFi Library**  
   - For ESP32 WiFi connectivity.  
   - Built-in with ESP32 core, or install via Board Manager.

2. **PubSubClient**  
   - For MQTT communication.  
   - Install via Arduino Library Manager:  
     ```
     Sketch > Include Library > Manage Libraries > Search for "PubSubClient"
     ```
3. **Ultrasonic sensor (URM-09)** 
   -For HC-SR04 ultrasonic sensor URM-09
   - Install via GitHub:  
     [[Ultrasonic](https://github.com/JRodrigoTech/Ultrasonic-HC-SR04](https://github.com/DFRobot/DFRobot_URM09))
     Search for "Adafruit Sensor"
     ```

### **Raspberry Pi Dependencies**
Install the following libraries or packages on your Raspberry Pi:

1. **I2C Communication**  
      first you must to active I2C Communication for raspberry pi
       1. "Sudo Raspi-config"
       2. Interface Options > I2C > Enable
     
4. **MQTT Library**
    Step two you must install MQTT library  
     sudo apt update
     sudo apt upgrade -y
     Sudo pip3 install paho-mqtt

3. **Sensor-Specific Libraries**  
   -For HC-SR04 ultrasonic sensor URM-09
   - Install via GitHub:  
     [[Ultrasonic](https://github.com/JRodrigoTech/Ultrasonic-HC-SR04](https://github.com/DFRobot/DFRobot_URM09))
   -for ADS115 Analog Digital Converter
    - Install via GitHub
      https://github.com/giobauermeister/ads1115-linux-rpi

### **Node-RED Dependencies**
Install the following custom nodes in Node-RED:

1. **Installation Steps:**  
    to use node-red with server for example install node-red in windows comment promt
    - npm install -g --unsafe-perm node-red
