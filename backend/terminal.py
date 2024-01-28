import subprocess
import threading
import os


class Terminal:
    def __init__(self, default_timeout=10):
        """ 
        Initialize the Terminal object.

        Parameters:
        - default_timeout (int): Default duration in seconds to wait before forcefully 
                                 terminating a command. 
        """
        self.latest_output = ""
        self.default_timeout = default_timeout
        self.current_dir = os.getcwd()

    def run_command(self, cmd, timeout=None):
        """
        Run a command and capture its output. If a timeout is not specified, use the default timeout.
        Also, handle the 'cd' command to change the current working directory.
        
        Parameters:
        - cmd (list): The command to run as a list of strings.
        - timeout (int): Optional. Duration in seconds to wait before forcefully terminating the command.

        Returns:
        - str: Merged stdout and stderr of the command.
        """

        # Handle 'cd' command separately
        if cmd[0] == "cd":
            try:
                # If the path is ~, expand it to the user's home directory
                target_dir = cmd[1] if cmd[1] != "~" else os.path.expanduser("~")
                new_dir = os.path.abspath(os.path.join(self.current_dir, target_dir))
                os.chdir(new_dir)
                self.current_dir = new_dir
                return ""
            except Exception as e:
                return str(e)

        def target():
            nonlocal combined_output
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.current_dir, check=True)
                combined_output = result.stdout + "\n" + result.stderr
            except subprocess.CalledProcessError as e:
                combined_output = e.stdout + "\n" + e.stderr

        combined_output = ""
        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout=timeout or self.default_timeout)
        if thread.is_alive():
            subprocess.run(['pkill', '-f', ' '.join(cmd)])
            thread.join()

        self.latest_output = combined_output
        return combined_output

    def get_latest_output(self):
        """Retrieve the output of the latest command."""
        return self.latest_output

    def get_current_directory(self):
        """Retrieve the current working directory."""
        return self.current_dir

    # You can add more methods as needed for your specific use case.

# Example usage:
terminal = Terminal(default_timeout=5)  # Setting a default timeout of 5 seconds

# Execute a cd command to change to the home directory
terminal.run_command(["cd", "~"])
print("Current Directory:", terminal.get_current_directory())