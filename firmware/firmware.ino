int controlPin = 8;

void setup() {
  Serial.begin(9600);
  pinMode(controlPin, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();

    if (command == '1') {
      digitalWrite(controlPin, HIGH);
      Serial.println("Pin is HIGH");
    } else if (command == '0') {
      digitalWrite(controlPin, LOW);
      Serial.println("Pin is LOW");
    } else {
      Serial.println("Invalid command");
    }
  }
}
