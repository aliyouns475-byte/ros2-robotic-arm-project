#include <Servo.h>

// Servo signal pins on Arduino Uno
const int PINS[4] = {9, 10, 11, 6};
Servo servos[4];
int angles[4] = {90, 90, 90, 90};

void setup() {
  Serial.begin(115200);
  for (int i = 0; i < 4; i++) {
    servos[i].attach(PINS[i]);
    servos[i].write(angles[i]);
  }
}

void loop() {
  if (Serial.available()) {
    // Expected line: "a1,a2,a3,a4\n" with each angle in 0..180
    String line = Serial.readStringUntil('\n');
    int v[4];
    int n = sscanf(line.c_str(), "%d,%d,%d,%d", &v[0], &v[1], &v[2], &v[3]);
    if (n == 4) {
      for (int i = 0; i < 4; i++) {
        angles[i] = constrain(v[i], 0, 180);
        servos[i].write(angles[i]);
      }
    }
  }
}
