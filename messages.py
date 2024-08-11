# messages.py

class Message:
    def __init__(self, role, content):
        self.role = role
        self.content = content

    def to_dict(self):
        """
        Convert the message to a dictionary format.
        """
        return {
            "role": self.role,
            "content": self.content
        }


class UserMessage(Message):
    def __init__(self, content):
        super().__init__(role="user", content=content)


class AIMessage(Message):
    def __init__(self, content="", tool_calls=None):
        super().__init__(role="assistant", content=content)
        self.tool_calls = tool_calls or []

    def to_dict(self):
        """
        Convert the AI message to a dictionary, including tool calls if present.
        """
        message_dict = super().to_dict()
        if self.tool_calls:
            message_dict["tool_calls"] = self.tool_calls
        return message_dict


class SystemMessage(Message):
    def __init__(self, content):
        super().__init__(role="system", content=content)


class ToolMessage(Message):
    def __init__(self, content, tool_call_id):
        super().__init__(role="tool", content=content)
        self.tool_call_id = tool_call_id

    def to_dict(self):
        """
        Convert the tool message to a dictionary, including the tool call ID.
        """
        message_dict = super().to_dict()
        message_dict["tool_call_id"] = self.tool_call_id
        return message_dict
