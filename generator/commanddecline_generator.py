"""
Decline message generator for Veyra.
Handles multi-argument command declines by producing a short,
sassy, persona-consistent message instructing the user to use
the correct slash/prefix command.
"""

from prompts.command_decline import create_command_decline_prompt

from state.client import client
# COMMAND_MAP maps internal command labels to their correct bot commands and a short description.



class CommandDeclineGenerator:
    """Generate decline messages for commands that require arguments."""
    def __init__(self):
        self.client = client

    async def generate(self, command: str) -> str:
        """
        Create a short, roasty decline message telling the user to use the proper command.

        Args:
            command (str): Internal command label predicted by the classifier.

        Returns:
            str: A persona-consistent decline message.
        """
        prompt = create_command_decline_prompt(command)

        try:
            response = await self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception:
            return "ugh—my brain lagged. ask properly again."