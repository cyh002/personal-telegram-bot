import os
from typing import Dict, Optional

class PromptManager:
    """Class for managing prompts loaded from files"""
    
    def __init__(self, prompts_dir: str = "prompts"):
        """Initialize the prompt manager with a directory of prompt files"""
        self.prompts_dir = prompts_dir
        self.prompts = {}
        self._load_prompts()
    
    def _load_prompts(self):
        """Load all prompt files from the prompts directory"""
        if not os.path.exists(self.prompts_dir):
            os.makedirs(self.prompts_dir)
            # Create a default prompt if directory is new
            with open(os.path.join(self.prompts_dir, "default.txt"), "w") as f:
                f.write("You are a helpful assistant. Keep replies within 20 words.")
                
        for filename in os.listdir(self.prompts_dir):
            if filename.endswith(".txt"):
                prompt_name = os.path.splitext(filename)[0]
                with open(os.path.join(self.prompts_dir, filename), "r") as f:
                    self.prompts[prompt_name] = f.read().strip()
    
    def get_prompt(self, name: str) -> Optional[str]:
        """Get a prompt by name"""
        return self.prompts.get(name)
    
    def list_prompts(self) -> Dict[str, str]:
        """List all available prompts"""
        return self.prompts
    
    def add_prompt(self, name: str, content: str) -> bool:
        """Add a new prompt or update an existing one"""
        try:
            with open(os.path.join(self.prompts_dir, f"{name}.txt"), "w") as f:
                f.write(content)
            self.prompts[name] = content
            return True
        except Exception as e:
            print(f"Error adding prompt: {e}")
            return False