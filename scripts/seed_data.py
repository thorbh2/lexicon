"""Seed LEXICON with a code of conduct + real posts on studionet (burner wallet)."""
from pathlib import Path
from gltest_cli.config.general import get_general_config
from gltest_cli.config.user import load_user_config
from gltest import get_contract_factory, get_default_account

ROOT = Path(__file__).resolve().parents[1]
cfg = load_user_config(str(ROOT / "gltest.config.yaml"))
get_general_config().user_config = cfg

ADDR = "0x069273ad89dEF184eaF83F36D67336DbF38948F8"

acct = get_default_account()
factory = get_contract_factory(contract_file_path=str(ROOT / "contracts" / "lexicon.py"))
contract = factory.build_contract(ADDR, account=acct)

CODE = ("Be respectful and constructive. Stay on the topic of GenLayer and "
        "decentralized AI. No spam, no hate speech, no personal attacks, no "
        "unrelated promotion. Share ideas, ask questions, and help others build.")

# set code (only if not already set)
existing = contract.get_code().call()
if not existing or not existing.strip():
    try:
        contract.set_code(args=[CODE]).transact()
        print("code set", flush=True)
    except Exception as e:
        print(f"set_code FAILED: {e}", flush=True)
else:
    print("code already set", flush=True)

posts = [
    "Just shipped my first Intelligent Contract that reads a live web page and reaches validator consensus on the result. The Equivalence Principle is wild once it clicks.",
    "Question: what's the best pattern for handling non-deterministic LLM output inside run_nondet_unsafe? Comparing normalized JSON keys has worked well for me.",
    "Sharing a small gas tip: batch your view reads in the frontend instead of one call per item — the studionet RPC handles it fine and the UI feels instant.",
    "Hot take: AI-moderated communities will out-scale human moderation because the rule set is transparent and every decision is auditable on-chain.",
    "BUY CHEAP FOLLOWERS NOW visit my link for 10000 followers fast guaranteed!!!",
]

for body in posts:
    try:
        contract.submit_post(args=[body]).transact()
        print(f"posted: {body[:45]}", flush=True)
    except Exception as e:
        print(f"FAILED: {e}", flush=True)

print("count=" + str(contract.get_post_count().call()), flush=True)
