import threading
import time
import numpy as np
from collections import deque
from core.controller import HybridController

class SimulationRunner:
    """
    Manages the control system simulation in a separate thread.
    Ensures precise timing and decouples physics from GUI rendering.
    """
    def __init__(self, max_points=200, dt=0.05):
        self.controller = HybridController()
        self.dt = dt
        self.max_points = max_points
        self.running = False
        self.thread = None
        self.lock = threading.Lock()
        
        # Simulation Parameters (Thread-safe access)
        self.target = 5.0
        
        # Data Buffers (Deque for efficient O(1) appends and fixed size)
        self.history = {
            "time": deque(maxlen=max_points),
            "target": deque(maxlen=max_points),
            "position": deque(maxlen=max_points),
            "velocity": deque(maxlen=max_points),
            "control": deque(maxlen=max_points),
            "alpha": deque(maxlen=max_points),
            "error": deque(maxlen=max_points),
            "p_term": deque(maxlen=max_points),
            "i_term": deque(maxlen=max_points),
            "d_term": deque(maxlen=max_points),
            "loss": deque(maxlen=max_points)
        }
        
        self.start_time = 0.0

    def start(self):
        if not self.running:
            self.running = True
            self.start_time = time.time()
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None

    def reset(self):
        was_running = self.running
        self.stop()
        
        with self.lock:
            self.controller.reset()
            for key in self.history:
                self.history[key].clear()
            self.start_time = time.time()
            
        if was_running:
            self.start()

    def set_target(self, value):
        self.target = value

    def set_pid_gains(self, kp, ki, kd):
        self.controller.set_pid_gains(kp, ki, kd)

    def set_noise(self, value):
        self.controller.set_noise(value)

    def set_mode(self, mode):
        self.controller.set_mode(mode)

    def _run_loop(self):
        """Main control loop running in background thread"""
        next_call = time.perf_counter()
        
        while self.running:
            # 1. Execute Control Step
            # We read self.target atomically (simple float)
            target = self.target
            
            # Step the controller
            pos, u, alpha, loss = self.controller.step(target, self.dt)
            
            # 2. Capture Telemetry
            current_time = time.time() - self.start_time
            vel = self.controller.plant.velocity
            error = target - pos
            
            # PID internals (accessing safely)
            pid = self.controller.pid
            p_term = pid.kp * error
            i_term = pid.ki * pid.integral
            d_term = pid.kd * ((error - pid.last_error)/self.dt if self.dt > 0 else 0)
            
            # 3. Update History (Thread-safe deque append)
            # Although deque is thread-safe for append/pop, we might want a lock 
            # if we want to ensure all lists are synced when reading.
            # For visualization, slight desync (one list having 1 more item) is usually fine.
            # But let's use a lock for correctness during read/write if needed.
            # For high perf, we can skip lock if we accept tearing, but let's be safe.
            with self.lock:
                self.history["time"].append(current_time)
                self.history["target"].append(target)
                self.history["position"].append(pos)
                self.history["velocity"].append(vel)
                self.history["control"].append(u)
                self.history["alpha"].append(alpha)
                self.history["error"].append(error)
                self.history["p_term"].append(p_term)
                self.history["i_term"].append(i_term)
                self.history["d_term"].append(d_term)
                self.history["loss"].append(loss)
            
            # 4. Precise Timing (Sleep until next tick)
            next_call = next_call + self.dt
            sleep_time = next_call - time.perf_counter()
            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                # Lagging behind, skip sleep to catch up (or reset base if too far)
                pass

    def get_history(self):
        """Return a snapshot of the history buffers"""
        with self.lock:
            # Convert to list to return a copy/snapshot for rendering
            return {k: list(v) for k, v in self.history.items()}
            
    def get_latest_metrics(self):
        """Return the most recent values for telemetry cards"""
        with self.lock:
            if not self.history["position"]:
                return {k: 0.0 for k in self.history}
            
            return {
                "Position": self.history["position"][-1],
                "Target": self.history["target"][-1],
                "Error": self.history["error"][-1],
                "Velocity": self.history["velocity"][-1],
                "Control (u)": self.history["control"][-1],
                "Loss": self.history["loss"][-1]
            }

    def get_radar_metrics(self):
        """Calculate system health metrics for the radar chart"""
        with self.lock:
            if len(self.history["error"]) < 10:
                return [0.8, 0.7, 0.9, 0.6, 0.8] # Default/Initial

            errors = np.array(self.history["error"])
            controls = np.array(self.history["control"])
            velocities = np.array(self.history["velocity"])
            
            # 1. Stability: Inverse of error variance (steadiness)
            stability = 1.0 / (1.0 + np.var(errors[-50:]))
            
            # 2. Response: Based on velocity magnitude (responsiveness)
            response = np.clip(np.mean(np.abs(velocities[-50:])) / 5.0, 0.2, 1.0)
            
            # 3. Accuracy: 1.0 - mean absolute error
            accuracy = np.clip(1.0 - np.mean(np.abs(errors[-50:])), 0.0, 1.0)
            
            # 4. Efficiency: Inverse of control effort
            efficiency = 1.0 / (1.0 + np.mean(np.abs(controls[-50:])) * 0.1)
            
            # 5. Robustness: Simulated metric (can be linked to disturbance rejection)
            robustness = 0.8 # Placeholder or complex calc
            
            return [stability, response, accuracy, efficiency, robustness]

    def get_fft_data(self):
        """Compute FFT of the error signal"""
        with self.lock:
            if len(self.history["error"]) < 20:
                return np.zeros(10)
                
            # Use last 64 points for FFT
            data = list(self.history["error"])[-64:]
            if len(data) < 64:
                return np.zeros(10)
                
            fft_vals = np.abs(np.fft.fft(data))[:10] # First 10 frequencies
            # Normalize
            fft_vals = fft_vals / (np.max(fft_vals) + 1e-6)
            return fft_vals
