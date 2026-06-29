"""Tests for LEXICON (direct runner, no network)."""
from pathlib import Path

CONTRACT = str(Path(__file__).resolve().parents[1] / "contracts" / "lexicon.py")
PENDING = 0; PUBLISHED = 1; REJECTED = 2
CODE = "Be respectful. No spam, no hate speech, no personal attacks."


def test_set_code(deploy, direct_vm, direct_alice):
    lex = deploy(CONTRACT)
    direct_vm.sender = direct_alice
    lex.set_code(CODE)
    assert lex.get_code() == CODE


def test_code_set_once(deploy, direct_vm, direct_alice, direct_bob):
    lex = deploy(CONTRACT)
    direct_vm.sender = direct_alice
    lex.set_code(CODE)
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("already set"):
        lex.set_code("different code")


def test_code_required_nonempty(deploy, direct_vm, direct_alice):
    lex = deploy(CONTRACT)
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("text is required"):
        lex.set_code("   ")


def test_submit_post(deploy, direct_vm, direct_alice, direct_bob):
    lex = deploy(CONTRACT)
    direct_vm.sender = direct_alice
    lex.set_code(CODE)
    direct_vm.sender = direct_bob
    pid = lex.submit_post("Hello everyone, excited to be here!")
    assert pid == 0
    assert lex.get_post_count() == 1
    p = lex.get_post(0)
    assert p["status"] == PENDING
    assert p["body"] == "Hello everyone, excited to be here!"


def test_submit_requires_code(deploy, direct_vm, direct_alice):
    lex = deploy(CONTRACT)
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("no code of conduct"):
        lex.submit_post("a post")


def test_submit_requires_body(deploy, direct_vm, direct_alice):
    lex = deploy(CONTRACT)
    direct_vm.sender = direct_alice
    lex.set_code(CODE)
    with direct_vm.expect_revert("body is required"):
        lex.submit_post("  ")


def test_multiple_posts(deploy, direct_vm, direct_alice, direct_bob):
    lex = deploy(CONTRACT)
    direct_vm.sender = direct_alice
    lex.set_code(CODE)
    direct_vm.sender = direct_bob
    lex.submit_post("first post")
    lex.submit_post("second post")
    lex.submit_post("third post")
    assert lex.get_post_count() == 3
    assert lex.get_post(1)["body"] == "second post"


def test_no_such_post(deploy, direct_vm, direct_alice):
    lex = deploy(CONTRACT)
    direct_vm.sender = direct_alice
    lex.set_code(CODE)
    with direct_vm.expect_revert("no such post"):
        lex.get_post(99)
