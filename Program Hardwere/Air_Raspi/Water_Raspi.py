import time
import json
import threading
import busio
import board
import paho.mqtt.client as mqtt
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_ads1x15.ads1015 import ADS1015
import sys
from queue import Queue
sys.path.append("/home/raspi/Projek air/python/raspberrypi")  
from DFRobot_URM09 import DFRobot_URM09_IIC

# Konstanta kalibrasi 
tegangan_ph7 = 1.5  
tegangan_ph4 = 2.03  
slope = (7.0 - 4.0) / (tegangan_ph7 - tegangan_ph4)
intercept = 7 - (slope * tegangan_ph7)  
running = threading.Event()
running.set()
data_queue = Queue()

# Konfigurasi MQTT
mqtt_broker = "........"  # Alamat broker MQTT
mqtt_topic = "........."        # Topik untuk data sensor
mqtt_delay_topic = "monitoringenergy/delay"  # Topik untuk delay pengiriman data
mqtt_username = "......"     # Username untuk autentikasi
mqtt_password = "........"  # Password untuk autentikasi
client = mqtt.Client()

# Variabel untuk mengatur delay pengiriman data
delay_time = 2  # Default delay 2 detik

# Fungsi untuk menangani koneksi ke broker MQTT
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Terhubung ke broker MQTT!")
        # Setelah terhubung, subscribe ke topik untuk delay
        client.subscribe(mqtt_delay_topic)
    else:
        print("Gagal terhubung ke broker MQTT, kode:", rc)

# Fungsi untuk menangani pesan yang diterima dari topik
def on_message(client, userdata, msg):
    global delay_time
    try:
        # Mengambil pesan yang diterima dan mengonversinya menjadi float
        message = float(msg.payload.decode())
        print(f"Menerima pesan baru untuk delay: {message} detik")
        # Update delay_time berdasarkan pesan yang diterima
        delay_time = message
    except ValueError:
        print(f"Pesan tidak valid diterima pada {msg.topic}: {msg.payload}")

# Fungsi untuk menghubungkan ke broker MQTT
def connect_mqtt():
    try:
        # Set username dan password untuk autentikasi
        client.username_pw_set(mqtt_username, mqtt_password)
        
        # Terhubung ke broker MQTT
        client.connect(mqtt_broker)
        client.on_connect = on_connect
        client.on_message = on_message
        client.loop_start()  # Memulai loop MQTT untuk menangani pengiriman dan penerimaan pesan
    except Exception as e:
        print(f"Gagal terhubung ke broker MQTT: {e}")

# Inisialisasi I2C dan sensor
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS1015(i2c)
chan_ph = AnalogIn(ads, 0)  # Sensor pH pada channel 0
turbidity_channel = AnalogIn(ads, 1)  # Sensor turbidity pada channel 1
urm09 = DFRobot_URM09_IIC(0x01, 0x11)

# Fungsi untuk mengonversi tegangan menjadi nilai pH
def konversi_tegangan_ke_ph(tegangan):
    return round(slope * tegangan + intercept, 2)

def baca_sensor_ads():
    while running.is_set():
        try:
            # Baca sensor pH dengan interval 2 detik
            tegangan_ph = chan_ph.voltage
            nilai_ph = konversi_tegangan_ke_ph(tegangan_ph)
            data_queue.put({"pH": nilai_ph})
            time.sleep(2)  # Interval pembacaan untuk pH

            # Baca sensor turbidity dengan interval 3 detik
            voltage_turbidity = turbidity_channel.voltage
            turbidity_value = (voltage_turbidity / 5.0) * 100
            data_queue.put({"turbidity": turbidity_value})
            time.sleep(3)  # Interval pembacaan untuk turbidity
        except Exception as e:
            print(f"Kesalahan membaca sensor ADS: {e}")

def baca_ultrasonik():
    while running.is_set():
        try:
            urm09.set_mode_range(urm09._MEASURE_MODE_AUTOMATIC, urm09._MEASURE_RANG_500)
            jarak = urm09.get_distance()
            if jarak is not None:
                data_queue.put({"jarak": jarak})
                time.sleep(2)  # Simulasi pembacaan setiap 2 detik
            else:
                print("Gagal membaca jarak, data None.")
        except Exception as e:
            print(f"Kesalahan membaca sensor ultrasonik: {e}")

# Fungsi untuk mengirim data ke broker MQTT
def kirim_data_mqtt(data):
    try:
        client.publish(mqtt_topic, json.dumps(data))
        print(f"Data dikirim ke MQTT: {json.dumps(data)}", end="\r")
    except Exception as e:
        print(f"Gagal mengirim data ke MQTT: {e}")

# Fungsi utama untuk menjalankan simulasi
def main():
    # Koneksi ke broker MQTT
    connect_mqtt()

    # Jalankan pembacaan sensor dalam thread terpisah
    threading.Thread(target=baca_sensor_ads).start()
    threading.Thread(target=baca_ultrasonik).start()
    
    # Loop utama untuk mengambil dan menampilkan data
    while running.is_set():
        try:
            # Membuat dictionary kosong untuk menyimpan data sensor yang lengkap
            data = {"pH": None, "jarak": None, "turbidity": None}
            
            # Mengisi data dari queue hingga semua sensor memiliki nilai
            while None in data.values():
                if not data_queue.empty():
                    # Update data dari queue jika ada yang baru
                    data.update(data_queue.get())
                    
                print(f"Data sensor: {json.dumps(data)}", end='\r')
                    
            # Flush output buffer untuk memastikan output langsung tampil
            sys.stdout.flush()
            
            # Kirim data ke broker MQTT
            kirim_data_mqtt(data)
            
            time.sleep(delay_time)  # Delay sesuai dengan nilai yang diterima dari MQTT
        except Exception as e:
            print(f"Kesalahan saat menjalankan PROGRAN: {e}")

if _name_ == "_main_":
    try:
        main()  # Memulai simulasi pembacaan sensor
    except KeyboardInterrupt:
        print("Menutup ")
        running.clear()
        client.loop_stop()  # Menghentikan loop MQTT
        time.sleep(3)  # Waktu untuk menghentikan semua thread
        print(" dihentikan.")