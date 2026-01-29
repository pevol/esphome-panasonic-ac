#include "esphome/components/climate/climate.h"
#include "esphome/components/climate/climate_mode.h"
#include "esphome/components/binary_sensor/binary_sensor.h"
#include "esppac.h"

namespace esphome {
namespace panasonic_ac {
namespace CNT {

static const uint8_t CTRL_HEADER = 0xF0;  // The header for control frames
static const uint8_t POLL_HEADER = 0x70;  // The header for the poll command

static const int POLL_INTERVAL = 5000;  // The interval at which to poll the AC
static const int CMD_INTERVAL = 250;    // The interval at which to send commands

// Cycling detection constants
static const int MAX_CYCLE_RECORDS = 20;  // Maximum number of cycles to track in ring buffer

enum class ACState {
  Initializing,  // Before first query response is receive
  Ready,         // All done, ready to receive regular packets
};

// Compressor state for cycling detection
enum class CompressorState {
  Unknown,  // Initial state, not yet determined
  On,       // Compressor is running (power >= on_threshold)
  Off       // Compressor is off (power <= off_threshold)
};

// Record of a single on/off cycle
struct CycleRecord {
  uint32_t timestamp;    // When the cycle ended (off transition)
  uint32_t on_duration;  // How long compressor was on (ms)
  uint32_t off_duration; // How long compressor was off before next on (ms), 0 if not yet known
};

class PanasonicACCNT : public PanasonicAC {
 public:
  void control(const climate::ClimateCall &call) override;

  void on_horizontal_swing_change(const std::string &swing) override;
  void on_vertical_swing_change(const std::string &swing) override;
  void on_nanoex_change(bool nanoex) override;
  void on_eco_change(bool eco) override;
  void on_econavi_change(bool eco) override;
  void on_mild_dry_change(bool mild_dry) override;

  void setup() override;
  void loop() override;

  // Cycling detection setters
  void set_cycling_detected_binary_sensor(binary_sensor::BinarySensor *sensor) { cycling_detected_sensor_ = sensor; }
  void set_cycle_count_sensor(sensor::Sensor *sensor) { cycle_count_sensor_ = sensor; }
  void set_avg_on_duration_sensor(sensor::Sensor *sensor) { avg_on_duration_sensor_ = sensor; }
  void set_avg_off_duration_sensor(sensor::Sensor *sensor) { avg_off_duration_sensor_ = sensor; }

  // Cycling detection threshold setters
  void set_cycling_power_on_threshold(uint16_t threshold) { power_on_threshold_ = threshold; }
  void set_cycling_power_off_threshold(uint16_t threshold) { power_off_threshold_ = threshold; }
  void set_cycling_min_on_duration(uint32_t duration) { min_on_duration_ = duration * 1000; }  // Convert s to ms
  void set_cycling_min_off_duration(uint32_t duration) { min_off_duration_ = duration * 1000; }  // Convert s to ms
  void set_cycling_time_window(uint32_t window) { time_window_ = window * 1000; }  // Convert s to ms
  void set_cycling_cycle_threshold(uint8_t threshold) { cycle_threshold_ = threshold; }

 protected:
  ACState state_ = ACState::Initializing;  // Stores the internal state of the AC, used during initialization

  // uint8_t data[10];
  std::vector<uint8_t> data = std::vector<uint8_t>(10);  // Stores the data received from the AC
  std::vector<uint8_t> cmd;                              // Used to build next command

  void handle_poll();
  void handle_cmd();

  void set_data(bool set);

  void send_command(std::vector<uint8_t> command, CommandType type, uint8_t header);
  void send_packet(const std::vector<uint8_t> &command, CommandType type);

  bool verify_packet();
  void handle_packet();

  // Cycling detection members
  binary_sensor::BinarySensor *cycling_detected_sensor_ = nullptr;
  sensor::Sensor *cycle_count_sensor_ = nullptr;
  sensor::Sensor *avg_on_duration_sensor_ = nullptr;
  sensor::Sensor *avg_off_duration_sensor_ = nullptr;

  // Cycling detection thresholds (with defaults)
  uint16_t power_on_threshold_ = 200;   // Power level indicating compressor running (W)
  uint16_t power_off_threshold_ = 100;  // Power level indicating compressor off (W)
  uint32_t min_on_duration_ = 30000;    // Minimum ON time to count as valid (ms)
  uint32_t min_off_duration_ = 30000;   // Minimum OFF time to count as valid (ms)
  uint32_t time_window_ = 600000;       // Window for counting cycles (ms)
  uint8_t cycle_threshold_ = 3;         // Cycles in window to trigger alert

  // Cycling detection state
  CompressorState compressor_state_ = CompressorState::Unknown;
  uint32_t state_start_time_ = 0;       // When current state started
  uint32_t last_on_start_ = 0;          // When compressor last turned on
  uint32_t last_on_duration_ = 0;       // Duration of last ON period

  // Cycle history ring buffer
  CycleRecord cycle_records_[MAX_CYCLE_RECORDS];
  uint8_t cycle_record_head_ = 0;       // Next write position
  uint8_t cycle_record_count_ = 0;      // Number of valid records

  // Cycling detection methods
  void process_power_for_cycling(uint16_t power);
  void record_cycle(uint32_t on_duration, uint32_t off_duration);
  uint8_t count_cycles_in_window();
  void update_cycling_sensors();
};

}  // namespace CNT
}  // namespace panasonic_ac
}  // namespace esphome
