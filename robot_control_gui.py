#!/usr/bin/env python3
"""
Police Robot Dog - Local GUI Control Program
A desktop application to control the robot dog locally.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import serial
import serial.tools.list_ports
import threading
import time
import logging
from datetime import datetime
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RobotControlGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Police Robot Dog Controller")
        self.root.geometry("600x700")
        self.root.resizable(True, True)
        
        # Serial connection
        self.arduino_serial = None
        self.connected = False
        self.last_command_time = 0
        
        # Create UI
        self.create_widgets()
        
        # Auto-connect disabled - user must manually click Connect button
        
        # Start connection monitor
        self.monitor_running = True
        self.monitor_thread = threading.Thread(target=self.connection_monitor, daemon=True)
        self.monitor_thread.start()
    
    def create_widgets(self):
        """Create all GUI widgets."""
        # Title
        title_frame = tk.Frame(self.root)
        title_frame.pack(pady=10)
        tk.Label(
            title_frame,
            text="🤖 Police Robot Dog Controller",
            font=("Arial", 18, "bold")
        ).pack()
        
        # Connection Status Frame
        status_frame = tk.LabelFrame(self.root, text="Connection Status", padx=10, pady=10)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_label = tk.Label(
            status_frame,
            text="● Disconnected",
            fg="red",
            font=("Arial", 12)
        )
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.port_label = tk.Label(
            status_frame,
            text="Port: None",
            font=("Arial", 10)
        )
        self.port_label.pack(side=tk.LEFT, padx=10)
        
        self.connect_btn = tk.Button(
            status_frame,
            text="Connect",
            command=self.toggle_connection,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            width=10
        )
        self.connect_btn.pack(side=tk.RIGHT, padx=5)
        
        # Port Selection
        port_frame = tk.LabelFrame(self.root, text="Arduino Port", padx=10, pady=10)
        port_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(
            port_frame,
            textvariable=self.port_var,
            width=30,
            state="readonly"
        )
        self.port_combo.pack(side=tk.LEFT, padx=5)
        self.port_combo.bind("<<ComboboxSelected>>", self.on_port_selected)
        
        refresh_btn = tk.Button(
            port_frame,
            text="Refresh",
            command=self.refresh_ports,
            width=10
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Control Buttons Frame
        control_frame = tk.LabelFrame(self.root, text="Movement Controls", padx=10, pady=10)
        control_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create button grid
        button_config = [
            ("", 0, 1),  # Empty top-left
            ("⬆ FORWARD", 0, 2, "FORWARD"),  # Top
            ("", 0, 3),  # Empty top-right
            ("⬅ LEFT", 1, 1, "LEFT"),  # Left
            ("⏹ STOP", 1, 2, "STOP"),  # Center
            ("➡ RIGHT", 1, 3, "RIGHT"),  # Right
            ("", 2, 1),  # Empty bottom-left
            ("⬇ BACKWARD", 2, 2, "BACKWARD"),  # Bottom
            ("", 2, 3),  # Empty bottom-right
        ]
        
        for btn_info in button_config:
            if len(btn_info) == 4:  # Has command
                text, row, col, command = btn_info
                # Create command function with proper closure
                def make_command(cmd):
                    def send():
                        self.log(f"DEBUG: Button clicked for command: {cmd}")
                        self.send_command(cmd)
                    return send
                
                btn = tk.Button(
                    control_frame,
                    text=text,
                    command=make_command(command),
                    font=("Arial", 14, "bold"),
                    width=12,
                    height=3,
                    bg="#2196F3",
                    fg="white",
                    activebackground="#1976D2"
                )
                if command == "STOP":
                    btn.config(bg="#f44336", activebackground="#d32f2f")
                btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        
        # Configure grid weights
        for i in range(3):
            control_frame.grid_columnconfigure(i, weight=1)
            control_frame.grid_rowconfigure(i, weight=1)
        
        # Log/Status Display
        log_frame = tk.LabelFrame(self.root, text="Log & Status", padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=8,
            font=("Courier", 9),
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
        # Clear log button
        clear_btn = tk.Button(
            log_frame,
            text="Clear Log",
            command=self.clear_log,
            width=10
        )
        clear_btn.pack(anchor=tk.E, pady=5)
        
        # Initial port refresh
        self.refresh_ports()
    
    def refresh_ports(self):
        """Refresh available serial ports."""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        
        # Prioritize Arduino port from config or find it automatically
        arduino_port = None
        
        # First, try the configured port
        if config.ARDUINO_PORT and config.ARDUINO_PORT in ports:
            arduino_port = config.ARDUINO_PORT
        
        # If not found, try to find Arduino by manufacturer
        if not arduino_port:
            port_list = list(serial.tools.list_ports.comports())
            for port in port_list:
                desc_lower = port.description.lower()
                man_lower = (port.manufacturer or "").lower()
                if "arduino" in desc_lower or "arduino" in man_lower:
                    if port.device in ports:
                        arduino_port = port.device
                        break
        
        # Set the port (Arduino if found, otherwise first available)
        if not self.port_var.get():
            if arduino_port:
                self.port_var.set(arduino_port)
                self.log(f"✓ Auto-selected Arduino port: {arduino_port}")
            elif ports:
                self.port_var.set(ports[0])
        
        self.log(f"Found {len(ports)} serial port(s): {', '.join(ports) if ports else 'None'}")
    
    def on_port_selected(self, event=None):
        """Handle port selection."""
        if self.connected:
            self.disconnect()
    
    def auto_connect(self):
        """Try to auto-connect to Arduino. (Disabled - user must click Connect)"""
        # Auto-connect disabled - user must manually click Connect button
        pass
    
    def find_arduino_port(self):
        """Find Arduino port automatically."""
        # Try configured port first
        if config.ARDUINO_PORT:
            try:
                test = serial.Serial(config.ARDUINO_PORT, config.ARDUINO_BAUD_RATE, timeout=1)
                test.close()
                return config.ARDUINO_PORT
            except:
                pass
        
        # Try to find Arduino by manufacturer/description
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            desc_lower = port.description.lower()
            man_lower = (port.manufacturer or "").lower()
            if "arduino" in desc_lower or "arduino" in man_lower:
                try:
                    test = serial.Serial(port.device, config.ARDUINO_BAUD_RATE, timeout=1)
                    test.close()
                    return port.device
                except:
                    continue
        
        # Try common ports (macOS and Linux)
        common_ports = [
            "/dev/cu.usbmodem*", "/dev/cu.usbserial*",  # macOS
            "/dev/ttyACM0", "/dev/ttyACM1",  # Linux
            "/dev/ttyUSB0", "/dev/ttyUSB1"   # Linux
        ]
        # Note: Can't use wildcards with Serial, so we'll check available ports
        available_ports = [p.device for p in ports]
        for common in ["/dev/ttyACM0", "/dev/ttyACM1", "/dev/ttyUSB0", "/dev/ttyUSB1"]:
            if common in available_ports:
                try:
                    test = serial.Serial(common, config.ARDUINO_BAUD_RATE, timeout=1)
                    test.close()
                    return common
                except:
                    continue
        
        # Return first available port
        return available_ports[0] if available_ports else None
    
    def connect(self):
        """Connect to Arduino."""
        port = self.port_var.get() or self.find_arduino_port()
        
        if not port:
            messagebox.showerror("Error", "No Arduino port selected or found!")
            return False
        
        try:
            self.arduino_serial = serial.Serial(
                port=port,
                baudrate=config.ARDUINO_BAUD_RATE,
                timeout=config.SERIAL_TIMEOUT,
                write_timeout=1.0
            )
            time.sleep(2)  # Wait for Arduino reset
            
            # Clear buffers
            self.arduino_serial.reset_input_buffer()
            self.arduino_serial.reset_output_buffer()
            
            # Wait for ready signal
            start_time = time.time()
            while time.time() - start_time < 3:
                if self.arduino_serial.in_waiting > 0:
                    try:
                        line = self.arduino_serial.readline().decode('utf-8', errors='ignore').strip()
                        if line and "ARDUINO_READY" in line:
                            self.log("✓ Arduino ready signal received")
                            break
                    except:
                        pass
                time.sleep(0.1)
            
            self.connected = True
            self.status_label.config(text="● Connected", fg="green")
            self.port_label.config(text=f"Port: {port}")
            self.connect_btn.config(text="Disconnect", bg="#f44336")
            self.log(f"✓ Connected to Arduino on {port}")
            return True
            
        except serial.SerialException as e:
            messagebox.showerror("Connection Error", f"Failed to connect:\n{e}")
            self.log(f"✗ Connection failed: {e}")
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error:\n{e}")
            self.log(f"✗ Error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Arduino."""
        if self.arduino_serial and self.arduino_serial.is_open:
            self.send_command("STOP")
            time.sleep(0.1)
            self.arduino_serial.close()
        
        self.connected = False
        self.arduino_serial = None
        self.status_label.config(text="● Disconnected", fg="red")
        self.port_label.config(text="Port: None")
        self.connect_btn.config(text="Connect", bg="#4CAF50")
        self.log("Disconnected from Arduino")
    
    def toggle_connection(self):
        """Toggle connection state."""
        if self.connected:
            self.disconnect()
        else:
            self.connect()
    
    def send_command(self, command):
        """Send command to Arduino."""
        if not self.connected or not self.arduino_serial:
            messagebox.showwarning("Not Connected", "Please connect to Arduino first!")
            return
        
        # Validate command
        if not command or command.strip() == "":
            self.log(f"✗ Error: Empty command")
            return
        
        try:
            command_bytes = (command + "\n").encode('utf-8')
            self.arduino_serial.write(command_bytes)
            self.arduino_serial.flush()
            
            self.last_command_time = time.time()
            self.log(f"→ Sent: {command}")
            
            # Read response
            start_time = time.time()
            response = ""
            while time.time() - start_time < config.SERIAL_TIMEOUT:
                if self.arduino_serial.in_waiting > 0:
                    try:
                        line = self.arduino_serial.readline().decode('utf-8', errors='ignore').strip()
                        if line:
                            response = line
                            break
                    except:
                        pass
                time.sleep(0.05)
            
            if response:
                if response.startswith("OK:"):
                    self.log(f"✓ Response: {response}")
                elif response.startswith("ERROR:"):
                    self.log(f"✗ Error: {response}")
            else:
                self.log(f"→ Command sent (no response)")
                
        except serial.SerialException as e:
            self.log(f"✗ Serial error: {e}")
            messagebox.showerror("Error", f"Communication error:\n{e}")
        except Exception as e:
            self.log(f"✗ Error: {e}")
            messagebox.showerror("Error", f"Unexpected error:\n{e}")
    
    def connection_monitor(self):
        """Monitor connection and implement failsafe."""
        while self.monitor_running:
            time.sleep(0.5)
            
            if self.connected and self.arduino_serial and self.arduino_serial.is_open:
                time_since_last = time.time() - self.last_command_time
                
                if self.last_command_time > 0 and time_since_last > config.COMMAND_TIMEOUT:
                    self.send_command("STOP")
                    self.log("⚠ Failsafe: Auto-stopped (no command for 2s)")
                    self.last_command_time = time.time()
    
    def log(self, message):
        """Add message to log display."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        logger.info(message)
    
    def clear_log(self):
        """Clear log display."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def on_closing(self):
        """Handle window closing."""
        self.monitor_running = False
        if self.connected:
            self.disconnect()
        self.root.destroy()


def main():
    """Main function."""
    root = tk.Tk()
    app = RobotControlGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()

