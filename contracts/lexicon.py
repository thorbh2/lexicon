# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""
LEXICON - AI-Moderated Community Feed
=====================================
A community runs a shared feed under a written code of conduct. Anyone submits a
post. Instead of a human moderator, the contract reads each post against the code
of conduct and the validator set agrees (Equivalence Principle) whether it is
acceptable. Accepted posts are published to the feed; rejected posts are held
back with a recorded reason. Every decision is on-chain and auditable.

Lifecycle for a post:
    PENDING   -> submitted, awaiting AI moderation
    PUBLISHED -> passed the code of conduct, visible on the feed
    REJECTED  -> violated the code of conduct, held back with a reason
"""

from genlayer import *
from dataclasses import dataclass
import json
import typing


STATUS_PENDING = 0
STATUS_PUBLISHED = 1
STATUS_REJECTED = 2


@allow_storage
@dataclass
class Post:
    author: Address
    body: str
    status: u8
    reason: str


class Lexicon(gl.Contract):
    code_of_conduct: str
    posts: DynArray[Post]

    def __init__(self) -> None:
        self.code_of_conduct = ""

    @gl.public.write
    def set_code(self, code: str) -> None:
        """Set the community code of conduct. Only allowed once (first writer
        becomes the steward)."""
        if len(self.code_of_conduct.strip()) != 0:
            raise gl.vm.UserError("code of conduct already set")
        if len(code.strip()) == 0:
            raise gl.vm.UserError("code of conduct text is required")
        self.code_of_conduct = code

    @gl.public.write
    def submit_post(self, body: str) -> int:
        if len(body.strip()) == 0:
            raise gl.vm.UserError("post body is required")
        if len(self.code_of_conduct.strip()) == 0:
            raise gl.vm.UserError("no code of conduct set yet")
        p = self.posts.append_new_get()
        p.author = gl.message.sender_address
        p.body = body
        p.status = u8(STATUS_PENDING)
        p.reason = ""
        return len(self.posts) - 1

    @gl.public.write
    def moderate(self, post_id: int) -> None:
        """The contract reads the post against the code of conduct and the
        validator set agrees whether to publish it."""
        p = self._get(post_id)
        if p.status != STATUS_PENDING:
            raise gl.vm.UserError("post already moderated")

        code = self.code_of_conduct
        body = p.body

        def leader_fn() -> str:
            prompt = (
                f"Community code of conduct:\n{code}\n\n"
                f"Submitted post:\n{body}\n\n"
                "As an impartial moderator, does this post comply with the code "
                "of conduct? Reply with ONLY JSON: {\"allow\": true} if it is "
                "acceptable, {\"allow\": false} if it violates the code, plus a "
                "short \"reason\"."
            )
            return gl.nondet.exec_prompt(prompt)

        def validator_fn(leader_res) -> bool:
            if not isinstance(leader_res, gl.vm.Return):
                return False
            return self._decision_of(leader_res.calldata)[0] == self._decision_of(leader_fn())[0]

        result = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)
        allow, reason = self._decision_of(result)
        p.reason = reason[:300]
        p.status = u8(STATUS_PUBLISHED if allow else STATUS_REJECTED)

    # ------------------------------------------------------------------ views
    @gl.public.view
    def get_code(self) -> str:
        return self.code_of_conduct

    @gl.public.view
    def get_post_count(self) -> int:
        return len(self.posts)

    @gl.public.view
    def get_post(self, post_id: int) -> dict:
        p = self._get(post_id)
        return {
            "author": p.author.as_hex,
            "body": p.body,
            "status": int(p.status),
            "reason": p.reason,
        }

    # -------------------------------------------------------------- internals
    def _get(self, post_id: int) -> Post:
        if post_id < 0 or post_id >= len(self.posts):
            raise gl.vm.UserError("no such post")
        return self.posts[post_id]

    def _decision_of(self, result: typing.Any) -> tuple:
        data = result
        if isinstance(data, str):
            data = self._extract_json(data)
        if not isinstance(data, dict):
            return (False, "")
        raw = data.get("allow", None)
        reason = str(data.get("reason", ""))
        if isinstance(raw, bool):
            return (raw, reason)
        if isinstance(raw, str):
            return (raw.strip().lower() == "true", reason)
        return (False, reason)

    def _extract_json(self, text: str) -> typing.Any:
        try:
            return json.loads(text)
        except (ValueError, TypeError):
            pass
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except (ValueError, TypeError):
                return None
        return None
