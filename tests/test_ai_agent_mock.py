from zenvx.ai_agent import agent


def test_mock_agent_returns_actions() -> None:
    ans = agent.answer('appimage fails', {'missing_dependencies': ['libfuse2']})
    assert ans['backend'] and isinstance(ans['actions'], list)
