import pytest
from unittest.mock import patch, MagicMock, mock_open
from src import utils

def test_checks_existing_files():
    with patch.object(utils.client.files, 'list', return_value=[1, 2, 3]):
        with patch('logging.info'):
            assert utils.checks_existing_files() == 3

def test_extract_content_video_youtube_channel(monkeypatch):
    mock_build = MagicMock()
    mock_youtube = MagicMock()
    mock_search = MagicMock()
    mock_search.list.return_value.execute.return_value = {
        'items': [
            {'id': {'videoId': 'abc'}, 'snippet': {'title': 'Title1'}},
            {'id': {'videoId': 'def'}, 'snippet': {'title': 'Title2'}}
        ]
    }
    mock_youtube.search.return_value = mock_search
    mock_build.return_value = mock_youtube

    monkeypatch.setattr(utils, 'build', mock_build)
    monkeypatch.setattr(utils, 'YOUTUBE_API_KEY', 'fake_key')
    with patch.object(utils, 'client'):
        with patch('builtins.open', mock_open()):
            with patch('time.sleep'):
                utils.extract_content_video_youtube(channel_id='chanid')

def test_extract_content_video_youtube_urls(monkeypatch):
    mock_build = MagicMock()
    mock_youtube = MagicMock()
    mock_videos = MagicMock()
    mock_videos.list.return_value.execute.return_value = {
        'items': [{'snippet': {'title': 'TitleX'}}]
    }
    mock_youtube.videos.return_value = mock_videos
    mock_build.return_value = mock_youtube

    monkeypatch.setattr(utils, 'build', mock_build)
    monkeypatch.setattr(utils, 'YOUTUBE_API_KEY', 'fake_key')
    with patch.object(utils, 'client'):
        with patch('builtins.open', mock_open()):
            with patch('time.sleep'):
                utils.extract_content_video_youtube(video_urls=['https://www.youtube.com/watch?v=abc'])

def test_extract_content_full_urls(monkeypatch):
    html = '<a href="/page1">Page1</a>'
    monkeypatch.setattr(utils.requests, 'get', lambda url: MagicMock(text=html))
    monkeypatch.setattr(utils, 'BeautifulSoup', lambda text, parser: MagicMock(find_all=lambda *a, **k: [MagicMock(__getitem__=lambda self, k: '/page1')]))
    monkeypatch.setattr(utils.os, 'makedirs', lambda path: None)
    monkeypatch.setattr(utils.os.path, 'exists', lambda path: False)
    with patch('builtins.open', mock_open()):
        utils.extract_content_full_urls()


def test_criar_agente_last_war(monkeypatch):
    monkeypatch.setattr(utils.client.files, 'list', lambda: [])
    mock_response = MagicMock(text="resposta curta")
    monkeypatch.setattr(utils.client.models, 'generate_content', lambda **kwargs: mock_response)
    with patch.object(utils.sentry_logger, 'info'):
        result = utils.criar_agente_last_war("Pergunta?")
        assert result == ["resposta curta"]


def test_user_add_source_data():
    with patch('builtins.open', mock_open()) as m:
        utils.user_add_source_data("testfile", "mensagem")
        m.assert_called_once()

def test_help_last_war():
    with patch('builtins.open', mock_open(read_data="conteudo")):
        assert utils.help_last_war() == "conteudo"