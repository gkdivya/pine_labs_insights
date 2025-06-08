import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class DataAnalysisAssistant:
    def __init__(self):
        """Initialize the OpenAI client and create an assistant"""
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.assistant = None
        self.thread = None
        self.file_id = None
        
    def create_assistant(self):
        """Create an assistant with code interpreter capabilities"""
        try:
            self.assistant = self.client.beta.assistants.create(
                name="Data Analysis Assistant",
                instructions="""You are a data analysis expert. You can analyze data files, 
                create visualizations, perform statistical analysis, and answer questions about data. 
                Always provide clear explanations along with your analysis.""",
                model="gpt-4o",  # or "gpt-4" or "gpt-3.5-turbo"
                tools=[{"type": "code_interpreter"}]
            )
            print(f"✅ Assistant created with ID: {self.assistant.id}")
            return self.assistant
        except Exception as e:
            print(f"❌ Error creating assistant: {e}")
            return None
    
    def upload_file(self, file_path):
        """Upload a file for analysis"""
        try:
            with open(file_path, "rb") as file:
                uploaded_file = self.client.files.create(
                    file=file,
                    purpose="assistants"
                )
            self.file_id = uploaded_file.id
            print(f"✅ File uploaded successfully. File ID: {self.file_id}")
            return self.file_id
        except Exception as e:
            print(f"❌ Error uploading file: {e}")
            return None
    
    def create_thread(self):
        """Create a conversation thread"""
        try:
            self.thread = self.client.beta.threads.create()
            print(f"✅ Thread created with ID: {self.thread.id}")
            return self.thread
        except Exception as e:
            print(f"❌ Error creating thread: {e}")
            return None
    
    def ask_question(self, question, include_file=True, show_steps=True):
        """Ask a question about the uploaded data and optionally show intermediate steps"""
        if not self.thread or not self.assistant:
            print("❌ Assistant or thread not initialized")
            return None
        
        try:
            # Prepare message content
            message_data = {
                "thread_id": self.thread.id,
                "role": "user",
                "content": question
            }
            
            # Add file attachment if requested and file exists
            if include_file and self.file_id:
                message_data["attachments"] = [
                    {
                        "file_id": self.file_id,
                        "tools": [{"type": "code_interpreter"}]
                    }
                ]
            
            # Create message
            message = self.client.beta.threads.messages.create(**message_data)
            
            # Run the assistant
            run = self.client.beta.threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id
            )
            
            # Wait for completion and show progress
            while run.status in ['queued', 'in_progress']:
                time.sleep(1)
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=self.thread.id,
                    run_id=run.id
                )
                if show_steps:
                    print(f"🔄 Status: {run.status}")
            
            if run.status == 'completed':
                # Show intermediate steps if requested
                if show_steps:
                    self._show_run_steps(run.id)
                
                # Get the response
                messages = self.client.beta.threads.messages.list(
                    thread_id=self.thread.id
                )
                
                # Return the latest assistant message
                for message in messages.data:
                    if message.role == "assistant":
                        response_text = ""
                        for content in message.content:
                            if content.type == "text":
                                response_text += content.text.value
                        return response_text
            else:
                print(f"❌ Run failed with status: {run.status}")
                return f"Error: Run failed with status {run.status}"
                
        except Exception as e:
            print(f"❌ Error asking question: {e}")
            return None
    
    def _show_run_steps(self, run_id):
        """Show the intermediate steps and code generated during the run"""
        try:
            run_steps = self.client.beta.threads.runs.steps.list(
                thread_id=self.thread.id,
                run_id=run_id
            )
            
            print("\n" + "="*60)
            print("🔍 INTERMEDIATE STEPS AND GENERATED CODE:")
            print("="*60)
            
            for i, step in enumerate(run_steps.data, 1):
                print(f"\n📍 Step {i}: {step.type}")
                print("-" * 40)
                
                if step.type == "tool_calls":
                    for tool_call in step.step_details.tool_calls:
                        if tool_call.type == "code_interpreter":
                            # Show the generated code
                            code_input = tool_call.code_interpreter.input
                            print(f"🐍 Generated Python Code:")
                            print(f"```python\n{code_input}\n```")
                            
                            # Show the outputs
                            outputs = tool_call.code_interpreter.outputs
                            if outputs:
                                print(f"\n📊 Code Output:")
                                for output in outputs:
                                    if output.type == "logs":
                                        print(f"📝 Logs: {output.logs}")
                                    elif output.type == "image":
                                        print(f"🖼️ Image generated: {output.image.file_id}")
                                    elif hasattr(output, 'text'):
                                        print(f"📄 Text: {output.text}")
                            else:
                                print("📝 No output logs")
                                
                elif step.type == "message_creation":
                    print(f"💬 Creating response message...")
                
                print("-" * 40)
            
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"⚠️ Could not retrieve run steps: {e}")
    
    def ask_question_with_detailed_steps(self, question, include_file=True):
        """Ask a question and get both the response and detailed step breakdown"""
        print(f"\n❓ Question: {question}")
        print("🔄 Processing...")
        
        response = self.ask_question(question, include_file, show_steps=True)
        
        if response:
            print(f"\n🤖 Final Response:")
            print("-" * 50)
            print(response)
            print("-" * 50)
        
        return response
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.assistant:
                self.client.beta.assistants.delete(self.assistant.id)
                print("✅ Assistant deleted")
            if self.file_id:
                self.client.files.delete(self.file_id)
                print("✅ File deleted")
        except Exception as e:
            print(f"⚠️ Error during cleanup: {e}")


