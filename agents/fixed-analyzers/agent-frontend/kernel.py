from typing import TypedDict, Annotated, List, Optional
import json, os
from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)
from plugins.TenKParser import TenKParserPlugin
from plugins.CallCenterRecordingParser import CallCenterRecordingParserPlugin

# Singleton class to manage Semantic Kernel and chat session
class ChatSingleton:
    _instance = None
    _initialized = False
    _kernel = None
    _chat_completion = None
    _history = None
    _execution_settings = None
    _agent = None
    
    @classmethod
    async def get_instance(cls):
        if cls._instance is None:
            cls._instance = ChatSingleton()
            await cls._instance._initialize()
        return cls._instance
    
    async def _initialize(self):
        if self._initialized:
            return
        
        #########################################
        # 1. Create the instance of the Kernel to register the plugin and service
        service_id = "agent"
        kernel = Kernel()
        kernel.add_plugin(TenKParserPlugin(), plugin_name="TenKParser")
        kernel.add_plugin(CallCenterRecordingParserPlugin(), plugin_name="CallCenterRecordingParser")
        kernel.add_service(AzureChatCompletion(service_id=service_id, deployment_name=os.getenv("AOAI_DEPLOYMENT_NAME"), base_url=os.getenv("AOAI_BASE_URL"), api_key=os.getenv("AOAI_KEY")))

        # 2. Configure the function choice behavior to auto invoke kernel functions
        # so that the agent can automatically execute the menu plugin functions when needed
        settings = kernel.get_prompt_execution_settings_from_service_id(service_id=service_id)
        settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

        # 3. Create the agent
        self._agent = ChatCompletionAgent(
            kernel=kernel,
            name="DataAnalyticsAgent",
            instructions=os.getenv("AGENT_PROMPT"),
            arguments=KernelArguments(settings=settings),
        )

        # 4. Create a chat history to hold the conversation
        self._history = ChatHistory()
        
        # Enable planning
        self._execution_settings = AzureChatPromptExecutionSettings()
        self._execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()  

        self._initialized = True
    
    def get_kernel(self):
        return self._kernel
    
    def get_chat_completion(self):
        return self._chat_completion
    
    def get_history(self):
        return self._history
    
    def get_execution_settings(self):
        return self._execution_settings
    
    def get_agent(self):
        return self._agent
    
    def clear_history(self):
        self._history = ChatHistory()

# Legacy function for backward compatibility, but now uses the singleton
async def init_kernel():
    chat_singleton = await ChatSingleton.get_instance()
    return (
        chat_singleton.get_kernel(),
        chat_singleton.get_chat_completion(),
        chat_singleton.get_history(),
        chat_singleton.get_execution_settings(),
        chat_singleton.get_agent()
    )
