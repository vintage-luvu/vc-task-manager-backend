import os
import json
from datetime import datetime
from typing import List, Dict, Any

# Google Calendar API 用のクライアントライブラリ
try:
    from googleapiclient.discovery import build  # type: ignore
    from google.oauth2.credentials import Credentials  # type: ignore
except ImportError:
    # google-api-python-client がインストールされていない場合のフォールバック
    build = None  # type: ignore
    Credentials = None  # type: ignore


def load_credentials() -> Any:
    """環境変数からGoogle OAuth認証情報を読み込み、Credentialsインスタンスを生成する。

    GOOGLE_CALENDAR_CREDENTIALS にJSON文字列をセットしておく必要があります。
    認証情報の作成は Google Cloud Console で行ってください。
    """
    creds_json = os.getenv("GOOGLE_CALENDAR_CREDENTIALS")
    if not creds_json or Credentials is None:
        return None
    try:
        creds_data = json.loads(creds_json)
    except json.JSONDecodeError:
        return None
    return Credentials.from_authorized_user_info(info=creds_data)


def get_calendar_events(max_results: int = 50) -> List[Dict[str, Any]]:
    """Google Calendarから今後の予定を取得する。

    認証情報が設定されていない場合は空リストを返す。
    """
    # google-api-python-client がインストールされていない場合は空リストを返す
    if build is None:
        return []
    creds = load_credentials()
    if not creds:
        return []
    service = build("calendar", "v3", credentials=creds)
    now = datetime.utcnow().isoformat() + "Z"
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])
    formatted = []
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        end = event["end"].get("dateTime", event["end"].get("date"))
        formatted.append(
            {
                "id": event.get("id"),
                "summary": event.get("summary"),
                "start": start,
                "end": end,
            }
        )
    return formatted


def find_free_slots(
    events: List[Dict[str, Any]], date_from: datetime, date_to: datetime
) -> List[Dict[str, Any]]:
    """予定のリストから空き時間帯を計算する。

    date_from から date_to までの間のイベントを基に、空き時間枠を返す。
    ここでは簡易実装としてイベント間のギャップをそのまま返却します。
    """
    # ISO文字列をdatetimeへ変換してソート
    sorted_events = sorted(events, key=lambda e: e["start"])
    free_slots: List[Dict[str, Any]] = []
    current_start = date_from
    for ev in sorted_events:
        try:
            ev_start = datetime.fromisoformat(ev["start"].replace("Z", "+00:00"))
        except Exception:
            ev_start = date_from
        if ev_start > current_start:
            free_slots.append({"start": current_start.isoformat(), "end": ev_start.isoformat()})
        try:
            ev_end = datetime.fromisoformat(ev["end"].replace("Z", "+00:00"))
        except Exception:
            ev_end = ev_start
        if ev_end > current_start:
            current_start = ev_end
    # 最終イベント後の空き時間
    if current_start < date_to:
        free_slots.append({"start": current_start.isoformat(), "end": date_to.isoformat()})
    return free_slots
