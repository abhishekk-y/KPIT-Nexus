import numpy as np
from core.rl_agent import DDPGAgent

class PIDController:
    """Optimized PID Controller with Anti-Windup"""
    def __init__(self, kp=2.0, ki=0.5, kd=0.1):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0.0
        self.last_error = 0.0
        
    def compute(self, error, dt):
        # Proportional
        P = self.kp * error
        
        # Integral with anti-windup
        self.integral += error * dt
        self.integral = np.clip(self.integral, -10.0, 10.0)
        I = self.ki * self.integral
        
        # Derivative
        derivative = (error - self.last_error) / dt if dt > 0 else 0.0
        D = self.kd * derivative
        self.last_error = error
        
        return P + I + D
    
    def reset(self):
        self.integral = 0.0
        self.last_error = 0.0


class MPCController:
    """Simplified Model Predictive Controller using Gradient Descent"""
    def __init__(self, horizon=10, dt=0.1):
        self.horizon = horizon
        self.dt = dt
        
    def compute(self, current_state, target, dt):
        """
        Simplified MPC using a grid search approach for low complexity.
        current_state: [position, velocity]
        """
        position, velocity = current_state
        best_u = 0.0
        min_cost = float('inf')
        
        # Search over control inputs
        for u in np.linspace(-10, 10, 41):  # 41 points for precision
            cost = self._predict_cost(position, velocity, u, target)
            if cost < min_cost:
                min_cost = cost
                best_u = u
                
        return best_u
    
    def _predict_cost(self, pos, vel, u, target):
        """Predict cost over horizon"""
        cost = 0.0
        p, v = pos, vel
        
        for _ in range(self.horizon):
            # Simple dynamics: acceleration = u - damping
            accel = u - 0.5 * v
            v += accel * self.dt
            p += v * self.dt
            
            # Cost: tracking error + control effort
            error = target - p
            cost += error**2 + 0.01 * u**2
            
        return cost


class PlantModel:
    """Second-Order System (e.g., DC Motor, Mass-Spring-Damper)"""
    def __init__(self):
        self.position = 0.0
        self.velocity = 0.0
        self.noise_level = 0.0
        
    def update(self, control_input, dt):
        """Update plant dynamics"""
        # Dynamics: x'' = u - 0.5*x' (damping) + disturbance
        disturbance = np.random.normal(0, self.noise_level) if self.noise_level > 0 else 0.0
        acceleration = control_input - 0.5 * self.velocity + disturbance
        self.velocity += acceleration * dt
        self.position += self.velocity * dt
        
    def reset(self):
        self.position = 0.0
        self.velocity = 0.0
    
    def set_noise(self, level):
        self.noise_level = level


class HybridController:
    """Adaptive Hybrid PID-MPC-RL Controller"""
    def __init__(self):
        self.pid = PIDController()
        self.mpc = MPCController()
        self.plant = PlantModel()
        
        # RL Agent (State: [pos, vel, target, error], Action: [u])
        self.rl_agent = DDPGAgent(state_dim=4, action_dim=1, max_action=10.0)
        self.mode = "HYBRID" # HYBRID, RL_TRAIN, RL_INFERENCE
        self.training_steps = 0
        
    def set_pid_gains(self, kp, ki, kd):
        self.pid.kp = kp
        self.pid.ki = ki
        self.pid.kd = kd
        
    def step(self, target, dt):
        """Execute one control step"""
        # 1. Calculate error
        error = target - self.plant.position
        
        # State for RL
        state = np.array([self.plant.position, self.plant.velocity, target, error])
        
        u_final = 0.0
        alpha = 0.0
        
        if self.mode == "RL_TRAIN" or self.mode == "RL_INFERENCE":
            # RL Control
            noise = 0.2 if self.mode == "RL_TRAIN" else 0.0
            action = self.rl_agent.select_action(state, noise)
            u_final = action[0]
            alpha = 0.0 # Pure RL
            
            # Train if in training mode
            if self.mode == "RL_TRAIN":
                # Calculate reward (negative squared error + penalty for effort)
                reward = -(error**2 + 0.01 * u_final**2)
                
                # Store transition (Next state is approximated for now, or we wait for next step? 
                # For simplicity in this sync loop, we'll predict next state or use a 1-step delay in a real loop.
                # Here we update plant immediately, so we can get next state.)
                
                # Update plant
                self.plant.update(u_final, dt)
                next_state = np.array([self.plant.position, self.plant.velocity, target, target - self.plant.position])
                done = False # Continuous task
                
                self.rl_agent.replay_buffer.add(state, action, reward, next_state, done)
                loss = self.rl_agent.train()
                self.training_steps += 1
                
                return self.plant.position, u_final, alpha, loss
                
        else:
            # Hybrid PID-MPC Control
            u_pid = self.pid.compute(error, dt)
            
            current_state_mpc = [self.plant.position, self.plant.velocity]
            u_mpc = self.mpc.compute(current_state_mpc, target, dt)
            
            # Adaptive Blending
            alpha = np.clip(np.abs(error) / 5.0, 0.0, 1.0)
            u_final = alpha * u_pid + (1 - alpha) * u_mpc
            u_final = np.clip(u_final, -10.0, 10.0)
            
            # Update plant
            self.plant.update(u_final, dt)
        
        return self.plant.position, u_final, alpha, 0.0
    
    def reset(self):
        self.pid.reset()
        self.plant.reset()
    
    def set_mode(self, mode):
        self.mode = mode
    
    def set_noise(self, level):
        self.plant.set_noise(level)

