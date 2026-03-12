"""
Help action generator.
Retrieves the most relevant knowledge sections via embeddings then calls
the LLM to produce a grounded, in-character answer.
"""

from generator.help_retriever import HelpRetriever
from prompts.help_prompt import help_prompt
from state.client import client
from openai import OpenAIError
from logger import logger


class HelpGenerator:
    def __init__(self) -> None:
        self.retriever = HelpRetriever()
        self.client = client

    async def generate(self, message: str, req_id: str, reason: str | None = None, prev_reply: str | None = None) -> str:
        # Use planner reason for retrieval — it's semantically resolved (e.g. follow-ups)
        retrieval_query = reason if reason else message
        logger.info(
            "[REQ: %s][HelpGenerator] message=%r  retrieval_query=%r  has_prev=%s",
            req_id, message, retrieval_query[:120], bool(prev_reply),
        )

        sections = await self.retriever.retrieve(retrieval_query, req_id=req_id, top_k=2)
        logger.info("[REQ: %s][HelpGenerator] %d section(s) injected into prompt", req_id, len(sections))

        prompt = help_prompt(message, sections, reason=reason, prev_reply=prev_reply)
        logger.debug("[REQ: %s][HelpGenerator] prompt length: %d chars", req_id, len(prompt))

        try:
            response = await self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=4000,
            )
            choice = response.choices[0]
            usage = response.usage
            logger.info(
                "[REQ: %s][HelpGenerator] finish_reason=%s  prompt_tokens=%s  completion_tokens=%s",
                req_id,
                choice.finish_reason,
                usage.prompt_tokens if usage else "?",
                usage.completion_tokens if usage else "?",
            )
            content = choice.message.content
            if not content:
                logger.warning(
                    "[REQ: %s][HelpGenerator] empty content — finish_reason=%s refusal=%s",
                    req_id,
                    choice.finish_reason,
                    getattr(choice.message, "refusal", None),
                )
                return "my memory's being weird right now — try asking again?"
            return content
        except OpenAIError as e:
            logger.error("[REQ: %s][HelpGenerator] error: %s", req_id, e)
            return "my memory's being weird right now — try asking again?"
