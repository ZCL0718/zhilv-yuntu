from scripts import debug_rag_retrieval as debug


def test_debug_retrieval_passes_destination(monkeypatch) -> None:
    captured = {}

    monkeypatch.setattr(
        debug,
        "build_destination_query",
        lambda **_: ("大理 拍照", {}),
    )

    def fake_retrieve(*, query, top_k, destination=None):
        captured.update(
            query=query,
            top_k=top_k,
            destination=destination,
        )
        usage = {"prompt_tokens": 0, "completion_tokens": 0}
        return [], usage, usage

    monkeypatch.setattr(
        debug,
        "retrieve_travel_guide_chunks",
        fake_retrieve,
    )
    monkeypatch.setattr(
        "sys.argv",
        ["debug_rag_retrieval.py", "--destination", "大理"],
    )

    assert debug.main() == 0
    assert captured["destination"] == "大理"