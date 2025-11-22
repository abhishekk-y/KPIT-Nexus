#include <math.h>
#include <stdlib.h>

// System State
typedef struct {
    double position;
    double velocity;
    double integral_error;
    double last_error;
} SystemState;

SystemState sys_state = {0.0, 0.0, 0.0, 0.0};

// PID Parameters
double Kp = 2.0;
double Ki = 0.5;
double Kd = 0.1;

// MPC Parameters
#define HORIZON 10
double dt = 0.1;

// External Assembly Function
extern double blend_signals(double pid_out, double mpc_out, double alpha);

// Exported functions for Python
__declspec(dllexport) void init_system() {
    sys_state.position = 0.0;
    sys_state.velocity = 0.0;
    sys_state.integral_error = 0.0;
    sys_state.last_error = 0.0;
}

__declspec(dllexport) void set_pid_params(double p, double i, double d) {
    Kp = p;
    Ki = i;
    Kd = d;
}

__declspec(dllexport) double get_position() {
    return sys_state.position;
}

// PID Controller Implementation
double compute_pid(double target, double dt) {
    double error = target - sys_state.position;
    sys_state.integral_error += error * dt;
    double derivative = (error - sys_state.last_error) / dt;
    sys_state.last_error = error;
    
    // Anti-windup
    if (sys_state.integral_error > 10.0) sys_state.integral_error = 10.0;
    if (sys_state.integral_error < -10.0) sys_state.integral_error = -10.0;

    return (Kp * error) + (Ki * sys_state.integral_error) + (Kd * derivative);
}

// Simplified MPC Implementation (Gradient Descent approach for low complexity)
double compute_mpc(double target, double dt) {
    double predicted_pos = sys_state.position;
    double predicted_vel = sys_state.velocity;
    double best_u = 0.0;
    double min_cost = 1e9;
    
    // Simple search for optimal control action
    // In a real rigorous system we would use a QP solver, but for "less complexity" 
    // and speed in this demo, we check a range of control inputs.
    for (double u = -10.0; u <= 10.0; u += 0.5) {
        double cost = 0.0;
        double p = predicted_pos;
        double v = predicted_vel;
        
        // Simulate forward
        for (int i = 0; i < HORIZON; i++) {
            double acceleration = u - 0.1 * v; // Simple dynamics: u - friction
            v += acceleration * dt;
            p += v * dt;
            
            double error = target - p;
            cost += error * error; // Minimize squared error
        }
        
        // Add control effort penalty
        cost += 0.1 * u * u;
        
        if (cost < min_cost) {
            min_cost = cost;
            best_u = u;
        }
    }
    return best_u;
}

// Plant Physics (Second Order System)
void update_physics(double u, double dt) {
    // Dynamics: x'' = u - 0.5*x' (Damping)
    double acceleration = u - 0.5 * sys_state.velocity;
    sys_state.velocity += acceleration * dt;
    sys_state.position += sys_state.velocity * dt;
}

// Main Step Function called by Python
__declspec(dllexport) void step_system(double target, double dt, double* out_pos, double* out_u, double* out_alpha) {
    // 1. Compute PID
    double u_pid = compute_pid(target, dt);
    
    // 2. Compute MPC
    double u_mpc = compute_mpc(target, dt);
    
    // 3. Compute Alpha (Adaptive Blending)
    // Large error -> Alpha close to 1 (PID)
    // Small error -> Alpha close to 0 (MPC)
    double error = fabs(target - sys_state.position);
    double alpha = error / 5.0; 
    if (alpha > 1.0) alpha = 1.0;
    if (alpha < 0.0) alpha = 0.0;
    
    // 4. Blend using Assembly function
    double u_final = blend_signals(u_pid, u_mpc, alpha);
    
    // Clamp output
    if (u_final > 10.0) u_final = 10.0;
    if (u_final < -10.0) u_final = -10.0;
    
    // 5. Update Physics
    update_physics(u_final, dt);
    
    // 6. Return values
    *out_pos = sys_state.position;
    *out_u = u_final;
    *out_alpha = alpha;
}
