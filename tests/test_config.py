from config import PROJECT_ROOT, ROOT_ENV_PATH, load_project_env


def test_root_env_is_the_only_project_env_path() -> None:
    assert ROOT_ENV_PATH == PROJECT_ROOT / ".env"
    assert load_project_env() == ROOT_ENV_PATH
