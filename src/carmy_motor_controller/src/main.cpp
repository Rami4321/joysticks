#include "motor_ros2/motor_cfg.h"
#include "carmy_motor_controller/msg/motor_motion_control.hpp"
#include "carmy_motor_controller/msg/motor_feedback.hpp"
#include "stdint.h"
#include <atomic>
#include <chrono>
#include <iostream>
#include <map>
#include <memory>
#include <mutex>
#include <rclcpp/node.hpp>
#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/string.hpp>
#include <thread>
#include <unistd.h>
#include <vector>

using MotorMotionControl = carmy_motor_controller::msg::MotorMotionControl;
using MotorFeedback = carmy_motor_controller::msg::MotorFeedback;

class MotorController : public rclcpp::Node {
public:
  MotorController(std::vector<uint8_t>& motor_ids, std::vector<int>& motor_types)
      : rclcpp::Node("motor_controller_node") {

        // Create mutually exclusive callback groups for multi-threading
        sub_cb_group_ = this->create_callback_group(rclcpp::CallbackGroupType::MutuallyExclusive);
        timer_cb_group_ = this->create_callback_group(rclcpp::CallbackGroupType::MutuallyExclusive);

        for (size_t i = 0; i < motor_ids.size(); ++i) {
          motors_.try_emplace(motor_ids[i], "can0", 0xFF, motor_ids[i], motor_types[i]);
        }

        for (auto& [id, motor] : motors_) {
          motor.Get_RobStrite_Motor_parameter(0x7005);
          usleep(1000);
          motor.enable_motor();
          usleep(1000);
        }

    auto sub_opt = rclcpp::SubscriptionOptions();
    sub_opt.callback_group = sub_cb_group_;

    motion_sub_ = this->create_subscription<MotorMotionControl>(
        "motion_control", 1,
        std::bind(&MotorController::motion_callback, this,
                  std::placeholders::_1), sub_opt);

    feedback_pub_ = this->create_publisher<MotorFeedback>("motor_feedback", 10);

    publish_timer_ = this->create_wall_timer(
        std::chrono::milliseconds(30),
        std::bind(&MotorController::hold_position, this), timer_cb_group_);
  }

  ~MotorController() {
    for (auto& [id, motor] : motors_) {
      motor.Disenable_Motor(0);
    }
  }

  void motion_callback(const MotorMotionControl::SharedPtr msg) {
    auto it = motors_.find(msg->motor_id);
    if (it == motors_.end()) {
      RCLCPP_WARN(this->get_logger(), "Motor ID %d not found", msg->motor_id);
      return;
    }

    // Lock the mutex to prevent race conditions with the CAN thread
    std::lock_guard<std::mutex> lock(target_mutex_);
    target_position_[msg->motor_id] = msg->position;
    target_velocity_[msg->motor_id] = msg->velocity;
    target_connected_[msg->motor_id] = true;
    target_kp_[msg->motor_id] = msg->kp;
    target_kd_[msg->motor_id] = msg->kd;
    target_torque_[msg->motor_id] = msg->torque;
  }

  void apply_target(uint8_t motor_id) {
    auto it = motors_.find(motor_id);
    if (it == motors_.end()) return;

    double t_pos, t_vel, t_kp, t_kd, t_tor;
    {
      // Lock mutex briefly to copy the freshest targets
      std::lock_guard<std::mutex> lock(target_mutex_);
      t_pos = target_position_[motor_id];
      t_vel = target_velocity_[motor_id];
      t_kp = target_kp_[motor_id];
      t_kd = target_kd_[motor_id];
      t_tor = target_torque_[motor_id];
    }

    auto [position_feedback, velocity_feedback, torque, temperature] =
        it->second.send_motion_command(t_tor, t_pos, t_vel, t_kp, t_kd);
    
    last_feedback_[motor_id].position = position_feedback;
    last_feedback_[motor_id].velocity = velocity_feedback;
    last_feedback_[motor_id].torque = torque;
    last_feedback_[motor_id].temperature = temperature;
  }

  void hold_position() {
    for (auto& [motor_id, motor] : motors_) {
      apply_target(motor_id);
    }
    publish_feedback();
  }

  void publish_feedback() {
    for (auto& [motor_id, motor] : motors_) {
      auto feedback = MotorFeedback();
      feedback.motor_id = motor_id;

      auto [position_feedback, velocity_feedback, torque, temperature] =
          motor.return_data_pvtt();

      if (position_feedback == 0.0 && velocity_feedback == 0.0 && torque == 0.0 && temperature == 0.0) {
        RCLCPP_WARN(this->get_logger(), "Motor %d is not detected!", motor_id);
        feedback.connected = false;
      } else {
        feedback.connected = true;
      }

      feedback.position = position_feedback;
      feedback.velocity = velocity_feedback;
      feedback.torque = torque;
      feedback.temperature = temperature;

      if (rclcpp::ok()) {
        feedback_pub_->publish(feedback);
      }
    }
  }

private:
  rclcpp::CallbackGroup::SharedPtr sub_cb_group_;
  rclcpp::CallbackGroup::SharedPtr timer_cb_group_;
  std::mutex target_mutex_;

  rclcpp::Subscription<MotorMotionControl>::SharedPtr motion_sub_;
  rclcpp::Publisher<MotorFeedback>::SharedPtr feedback_pub_;
  rclcpp::TimerBase::SharedPtr publish_timer_;

  std::map<uint8_t, RobStrideMotor> motors_;
  std::map<uint8_t, double> target_position_;
  std::map<uint8_t, double> target_velocity_;
  std::map<uint8_t, double> target_kp_;
  std::map<uint8_t, double> target_kd_;
  std::map<uint8_t, double> target_torque_;
  std::map<uint8_t, bool> target_connected_;

  struct MotionFeedback {
    bool connected = false;
    double position = 0.0;
    double velocity = 0.0;
    double torque = 0.0;
    double temperature = 0.0;
  };
  std::map<uint8_t, MotionFeedback> last_feedback_;
};

int main(int argc, char **argv) {
  std::vector<uint8_t> motor_ids = {0x01, 0x02, 0x03, 0x04};
  std::vector<int> motor_types = {4, 4, 4, 4}; 

  rclcpp::init(argc, argv);
  auto controller = std::make_shared<MotorController>(motor_ids, motor_types);
  
  // Use a MultiThreadedExecutor so CAN timeouts cannot starve the network subscriber
  rclcpp::executors::MultiThreadedExecutor executor;
  executor.add_node(controller);
  executor.spin();

  rclcpp::shutdown();
  return 0;
}