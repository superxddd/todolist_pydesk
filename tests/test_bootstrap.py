from ai_todo.app.bootstrap import build_application


def test_build_application_creates_context(tmp_path):
    context = build_application(test_mode=True, data_root=tmp_path)
    assert context.repository.list()
    assert context.config.paths.tasks_file.exists()
