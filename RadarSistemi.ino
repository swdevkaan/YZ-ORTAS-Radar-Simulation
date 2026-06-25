#include <Servo.h>

Servo myServo;
int pos = 0;
int yon = 1; // 1 ileri, -1 geri döner
bool radarDonuyorMu = true; // Başlangıçta dönsün

const int trigPin = 9;
const int echoPin = 10;
long duration;
int distance;

void setup() {
  Serial.begin(115200);
  myServo.attach(11); // Servo pinini kendi devrene göre değiştir
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
}

void loop() {
  // PYTHON'DAN GELEN KOMUTLARI DİNLE
  if (Serial.available() > 0) {
    char komut = Serial.read();
    if (komut == 'S') { // S: Stop (Dur)
      radarDonuyorMu = false;
    } 
    else if (komut == 'R') { // R: Run (Tekrar Dönmeye Başla)
      radarDonuyorMu = true;
    }
  }

  // SADECE İZİN VARSA RADARI DÖNDÜR
  if (radarDonuyorMu) {
    pos += yon;
    if (pos >= 180 || pos <= 0) {
      yon = -yon; // Sona gelince yön değiştir
    }
    myServo.write(pos);
    delay(30); // Motor hızı
  }
  
  // HER HALÜKARDA MESAFEYİ ÖLÇ VE PYTHON'A GÖNDER
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  duration = pulseIn(echoPin, HIGH);
  distance = duration * 0.034 / 2;
  
  // Python'un okuyacağı format (Açı,Mesafe.)
  Serial.print(pos);
  Serial.print(",");
  Serial.print(distance);
  Serial.println(".");
}