import os
import sys
import json
import requests

# Import required modules for creating the GUI
try:
    import tkinter as tk
    from tkinter import ttk
    from tkinter import scrolledtext
    from tkinter import messagebox
except ModuleNotFoundError as e:
    # If tkinter is not installed, print an error and exit
    print(f"Error: {e}. Please ensure all required modules are installed.")
    sys.exit(1)

class LLMGUI:
    def __init__(self, root):
        # Initialize the main application window
        self.root = root
        root.title("LLM GUI")

        # Input field for the OpenRouter API Key
        api_key_label = ttk.Label(root, text="OpenRouter API Key:")
        api_key_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.api_key_entry = ttk.Entry(root, show="*")  # Hide API key for security
        self.api_key_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Pre-fill API key from environment variable if available
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if self.api_key:
            self.api_key_entry.insert(0, "*" * len(self.api_key))  # Mask the API key

        # Dropdown for selecting the model
        model_label = ttk.Label(root, text="Select Model:")
        model_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.model_var = tk.StringVar(root)  # Variable to hold selected model
        self.model_var.set("")  # Set default model to empty string
        self.model_dropdown = ttk.Combobox(root, textvariable=self.model_var, values=[])
        self.model_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Text area for user input
        input_label = ttk.Label(root, text="Input:")
        input_label.grid(row=2, column=0, padx=5, pady=5, sticky="nw")

        self.input_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=10)  # Enable text wrapping
        self.input_text.grid(row=2, column=1, padx=5, pady=5, sticky="nsew")

        # Text area for displaying output
        output_label = ttk.Label(root, text="Output:")
        output_label.grid(row=3, column=0, padx=5, pady=5, sticky="nw")

        self.output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=10, state=tk.DISABLED)  # Read-only
        self.output_text.grid(row=3, column=1, padx=5, pady=5, sticky="nsew")

        # Progress bar for loading indication
        self.progress_bar = ttk.Progressbar(root, mode='indeterminate')
        self.progress_bar.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        self.progress_bar.grid_remove()  # Initially hide the progress bar

        # Button to send the API request
        send_button = ttk.Button(root, text="Send", command=self.send_request)
        send_button.grid(row=5, column=1, padx=5, pady=5, sticky="e")
        self.send_button = send_button # Store the button as an instance variable

        # Configure grid layout to make widgets resize dynamically
        root.columnconfigure(1, weight=1)
        root.rowconfigure(2, weight=1)
        root.rowconfigure(3, weight=1)

    def update_model_list(self):
        # Fetch the list of available models from the OpenRouter API
        try:
            response = requests.get("https://openrouter.ai/api/v1/models")
            response.raise_for_status()  # Raise an exception for bad status codes
            models_data = response.json()
            models = [model["id"] for model in models_data["data"]]
            self.model_dropdown['values'] = models
            if models:
                self.model_var.set(models[0]) # Set the first model as default
        except requests.exceptions.RequestException as e:
            print(f"Error fetching models: {e}")
            self.model_dropdown['values'] = ["Error fetching models"]
            self.model_var.set("Error fetching models")
            if self.root:
                messagebox.showerror("Error", f"Error fetching models. Please check your network connection and try again. Details: {e}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
            self.model_dropdown['values'] = ["Error fetching models"]
            self.model_var.set("Error fetching models")
            if self.root:
                messagebox.showerror("Error", f"Error decoding JSON response when fetching models. Please check the API endpoint. Details: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            self.model_dropdown['values'] = ["Error fetching models"]
            self.model_var.set("Error fetching models")
            if self.root:
                messagebox.showerror("Error", f"An unexpected error occurred when fetching models. Details: {e}")


    def send_request(self):
        # Disable the send button and show the progress bar
        self.send_button.config(state=tk.DISABLED)
        self.progress_bar.grid()
        self.progress_bar.start()

        # Retrieve the API key, selected model, and user input
        api_key = self.api_key or self.api_key_entry.get()
        model = self.model_var.get()
        input_text = self.input_text.get("1.0", tk.END).strip()  # Remove trailing spaces

        if not api_key or not model or not input_text:
            # Handle missing API key, model, or input text
            output = "Error: API key, model, or input text is missing."
            self.display_output(output)
            self.reset_ui()
            return
        
        try:
            # Prepare headers and data payload for the API request
            headers = {
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://your-site-url.com",  # Optional header for rankings
                "X-Title": "Your App Name",  # Optional header for app name
            }
            data = {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": input_text
                    }
                ]
            }

            # Send a POST request to the OpenRouter API
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                data=json.dumps(data)
            )

            if response.status_code == 200:
                # Parse the successful response and extract the output
                result = response.json()
                if "choices" in result:
                    output = result["choices"][0]["message"]["content"].strip()
                else:
                    print(f"Error: 'choices' key not found in API response: {result}")
                    output = f"Error: 'choices' key not found in API response. Please check the API response structure."
            else:
                try:
                    error_data = response.json()
                    if "error" in error_data and "message" in error_data["error"]:
                        output = f"Error: {response.status_code} - {error_data['error']['message']}"
                    else:
                        output = f"Error: {response.status_code} - {response.text}"
                except json.JSONDecodeError:
                    output = f"Error: {response.status_code} - {response.text}"


        except Exception as e:
            # Catch and display exceptions
            output = f"Error: {e}"
        
        self.display_output(output)
        self.reset_ui()

    def display_output(self, output):
        # Display the output in the read-only text area
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, output)
        self.output_text.config(state=tk.DISABLED)

    def reset_ui(self):
        # Stop the progress bar and hide it
        self.progress_bar.stop()
        self.progress_bar.grid_remove()
        # Enable the send button
        self.send_button.config(state=tk.NORMAL)

if __name__ == "__main__":
    # Create the main application window and start the event loop
    root = tk.Tk()
    gui = LLMGUI(root)
    root.after(0, gui.update_model_list)
    root.mainloop()
