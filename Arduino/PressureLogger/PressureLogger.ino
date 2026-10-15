// PressureLogger.ino
// Reads two pressure transducers, converts voltage -> pressure using
// calibration equations derived from CalibrationCurve.m, and streams
// timestamped CSV data over Serial at 5 Hz (one sample every 200 ms).
//
// Wiring:
//   Sensor 1 (500 PSI transducer) analog output -> A0
//   Sensor 2 (300 PSI transducer) analog output -> A1
//   Verify each sensor's supply and output limits against its exact model
//   before wiring; the analog outputs must stay within the Uno's 0-5V range.
//
// Output format (one line per sample):
//   time_ms,V1,P1,V2,P2

const int SENSOR1_PIN = A0;
const int SENSOR2_PIN = A1;

// Sampling period in ms. 200 ms = 5 Hz.
const unsigned long SAMPLE_PERIOD_MS = 200;

// Calibration constants from CalibrationCurve.m (V = m*P + b  ->  P = (V-b)/m)
const float M1 = 0.016089285714285705;   // Sensor 1 slope (V/PSI)
const float INTERCEPT_1 = -0.008214285714285886;  // Sensor 1 intercept (V)

const float M2 = 0.04635714285714283;    // Sensor 2 slope (V/PSI)
const float INTERCEPT_2 = -0.05857142857142892;   // Sensor 2 intercept (V)


const float ADC_REF_VOLTAGE = 5.0;
const float ADC_MAX_COUNTS  = 1023.0;

unsigned long lastSampleTime = 0;
unsigned long startTime = 0;

void setup() {
  Serial.begin(9600);
  while (!Serial) { ; }

  startTime = millis();
  lastSampleTime = startTime;

  // Header row for the CSV file
  Serial.println("time_ms,V1,P1_psi,V2,P2_psi");
}

void loop() {
  unsigned long now = millis();

  if (now - lastSampleTime >= SAMPLE_PERIOD_MS) {
    lastSampleTime = now;

    int raw1 = analogRead(SENSOR1_PIN);
    int raw2 = analogRead(SENSOR2_PIN);

    float v1 = raw1 * (ADC_REF_VOLTAGE / ADC_MAX_COUNTS);
    float v2 = raw2 * (ADC_REF_VOLTAGE / ADC_MAX_COUNTS);

    float p1 = (v1 - INTERCEPT_1) / M1;
    float p2 = (v2 - INTERCEPT_2) / M2;

    unsigned long elapsed = now - startTime;

    Serial.print(elapsed);
    Serial.print(",");
    Serial.print(v1, 4);
    Serial.print(",");
    Serial.print(p1, 3);
    Serial.print(",");
    Serial.print(v2, 4);
    Serial.print(",");
    Serial.println(p2, 3);
  }
}
