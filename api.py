from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
import traceback

from agent import agent
from google.genai.types import Content, Part
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from bq.bq import BQClient

# Global session service and session cache for persistence across turns
session_service = InMemorySessionService()
session_cache = {}

# BigQuery client for anomaly endpoints
bq_client = BQClient()

# -----------------------------------------------------------------------------
# App setup
# -----------------------------------------------------------------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)

# -----------------------------------------------------------------------------
# Models
# -----------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str

# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------


@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        # Build user message
        user_content = Content(
            role="user",
            parts=[Part(text=req.message)]
        )

        # Use a fixed user/session_id for demo; in production, use real user/session
        user_id = "user"
        session_id = "chat_session"

        # Reuse session if it exists, else create new
        if session_id in session_cache:
            session = session_cache[session_id]
        else:
            session = await session_service.create_session(
                app_name="click_inflation_app",
                user_id=user_id,
                state={},
                session_id=session_id
            )
            session_cache[session_id] = session

        runner = Runner(app_name="click_inflation_app", agent=agent, session_service=session_service)

        import logging
        responses = []
        sql_executed = False
        db_result_rows = None

        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=user_content
        ):
            # Log event for debugging
            logging.debug(f"Event: {event}")
            if (
                hasattr(event, "content")
                and event.content
                and hasattr(event.content, "parts")
                and event.content.parts
                and hasattr(event.content.parts[0], "text")
                and event.content.parts[0].text
            ):
                responses.append(event.content.parts[0].text)
            # Check for DB execution result in orchestrator state
            if hasattr(event, "author") and event.author == "root":
                # Try to extract db_result from session state
                db_output = session.state.get("db_output")
                if db_output and "rows" in db_output:
                    sql_executed = True
                    db_result_rows = db_output["rows"]

        logging.debug(f"Events collected: {len(responses)}")
        logging.debug(f"SQL executed: {sql_executed}")
        logging.debug(f"DB result rows: {db_result_rows}")

        # If SQL executed but no Event was yielded, return a minimal response
        if sql_executed and not responses:
            return {
                "content": {
                    "parts": [
                        {"text": f"Query executed. Rows: {len(db_result_rows) if db_result_rows is not None else 0}"}
                    ]
                },
                "rows": db_result_rows or []
            }

        final_answer = responses[-1] if responses else "No results found."

        # Check if this is an anomaly query - if so, fetch chart data
        has_anomaly_chart = False
        chart_data = None
        
        if any(keyword in final_answer.lower() for keyword in ["anomaly", "anomalies", "spike", "outlier", "abnormal"]):
            # Replace the technical response with a user-friendly message
            final_answer = "Anomaly Detection Complete - Displaying dashboard below"
            try:
                # Fetch top 10 anomalies
                top10_sql = """
                    SELECT media_source, event_hour_anomaly, mean_3d, std_3d, cv
                    FROM `practicode-2025.clicks_data_prac.media_source_anomaly_cv_top_10`
                    ORDER BY cv DESC
                """
                top10_rows = bq_client.execute_query(top10_sql, "top10_for_chat")
                media_sources = []
                for index, row in enumerate(top10_rows):
                    media_sources.append({
                        "id": index + 1,
                        "media_source": row.media_source,
                        "hr": row.event_hour_anomaly,
                        "mean_3d": float(row.mean_3d),
                        "std_3d": float(row.std_3d),
                        "cv": float(row.cv)
                    })
                
                # Fetch all clicks data
                all_clicks_sql = """
                    SELECT media_source, event_date, event_hour, total_clicks
                    FROM `practicode-2025.clicks_data_prac.media_source_anomaly_all_clicks`
                    ORDER BY media_source, event_date, event_hour
                """
                all_clicks_rows = bq_client.execute_query(all_clicks_sql, "all_clicks_for_chat")
                clicks_data = [dict(row.items()) for row in all_clicks_rows]
                
                # Group by media_source for level2
                grouped = {}
                for item in clicks_data:
                    media = item["media_source"]
                    if media not in grouped:
                        grouped[media] = []
                    grouped[media].append(item)
                
                # Fetch app-level data for drill-down (level3)
                app_sql = """
                    SELECT media_source, event_date, event_hour, app_id, total_clicks
                    FROM `practicode-2025.clicks_data_prac.media_source_anomaly_app_root_cause`
                    ORDER BY media_source, event_date, event_hour, app_id
                """
                app_rows = bq_client.execute_query(app_sql, "app_level_for_chat")
                app_data = [dict(row.items()) for row in app_rows]
                
                # Group by media_source + event_date + event_hour for level3
                app_grouped = {}
                for item in app_data:
                    key = f"{item['media_source']}_{item['event_date']}_{item['event_hour']}"
                    if key not in app_grouped:
                        app_grouped[key] = []
                    app_grouped[key].append(item)
                
                chart_data = {
                    "level1": {"media_sources": media_sources},
                    "level2": grouped,
                    "level3": app_grouped
                }
                has_anomaly_chart = True
                logging.info("✅ Fetched chart data for anomaly response")
            except Exception as chart_error:
                logging.error(f"Failed to fetch chart data: {chart_error}")
                has_anomaly_chart = False

        return {
            "content": {
                "parts": [
                    {"text": final_answer}
                ]
            },
            "rows": db_result_rows or [] if sql_executed else None,
            "has_chart": has_anomaly_chart,
            "chart_data": chart_data
        }

    except Exception as e:
        # Log full traceback for debugging
        logging.error("Exception in /chat endpoint")
        logging.error(traceback.format_exc())

        # Return structured JSON error (no crash)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(e)
            }
        )


@app.get("/health")
def health():
    return {"ok": True}


# -----------------------------------------------------------------------------
# Anomaly Dashboard Endpoints
# -----------------------------------------------------------------------------

from fastapi import Query

@app.get("/api/anomalies/top10")
def get_top10_anomalies(media: str = Query(None)):
    """
    Returns top 10 anomalies by CV (Coefficient of Variation).
    
    Returns:
        dict: Data structure compatible with React component
    """
    try:
        if media == "partner":
            sql = """
                SELECT partner, event_hour_anomaly, mean_3d, std_3d, cv
                FROM `practicode-2025.clicks_data_prac.partner_anomaly_cv_top_10`
                ORDER BY cv DESC
            """
        else:
            sql = """
                SELECT media_source, event_hour_anomaly, mean_3d, std_3d, cv
                FROM `practicode-2025.clicks_data_prac.media_source_anomaly_cv_top_10`
                ORDER BY cv DESC
            """
        rows = bq_client.execute_query(sql, "top10_anomalies")
        # Convert data to structure suitable for component
        media_sources = []
        for index, row in enumerate(rows):
            if media == "partner":
                media_sources.append({
                    "id": index + 1,
                    "media_source": row.partner,
                    "hr": row.event_hour_anomaly,
                    "mean_3d": float(row.mean_3d),
                    "std_3d": float(row.std_3d),
                    "cv": float(row.cv)
                })
            else:
                media_sources.append({
                    "id": index + 1,
                    "media_source": row.media_source,
                    "hr": row.event_hour_anomaly,
                    "mean_3d": float(row.mean_3d),
                    "std_3d": float(row.std_3d),
                    "cv": float(row.cv)
                })
        return {
            "level1": {
                "media_sources": media_sources
            }
        }
    except Exception as e:
        logging.error(f"Error in get_top10_anomalies: {e}")
        # Return mock data if BigQuery fails
        return {
            "level1": {
                "media_sources": [
                    {"id": 1, "media_source": "facebook_int", "hr": 14, "mean_3d": 1250.5, "std_3d": 450.2, "cv": 2.35},
                    {"id": 2, "media_source": "google_int", "hr": 18, "mean_3d": 980.3, "std_3d": 380.1, "cv": 2.12},
                    {"id": 3, "media_source": "tiktok_int", "hr": 20, "mean_3d": 750.8, "std_3d": 320.5, "cv": 1.95},
                    {"id": 4, "media_source": "snapchat_int", "hr": 16, "mean_3d": 680.2, "std_3d": 290.4, "cv": 1.87},
                    {"id": 5, "media_source": "twitter_int", "hr": 19, "mean_3d": 520.6, "std_3d": 245.8, "cv": 1.72},
                    {"id": 6, "media_source": "instagram_int", "hr": 15, "mean_3d": 890.3, "std_3d": 410.5, "cv": 1.65},
                    {"id": 7, "media_source": "linkedin_int", "hr": 10, "mean_3d": 340.8, "std_3d": 180.2, "cv": 1.52},
                    {"id": 8, "media_source": "pinterest_int", "hr": 13, "mean_3d": 280.5, "std_3d": 145.3, "cv": 1.45},
                    {"id": 9, "media_source": "reddit_int", "hr": 21, "mean_3d": 420.7, "std_3d": 220.1, "cv": 1.38},
                    {"id": 10, "media_source": "youtube_int", "hr": 17, "mean_3d": 950.2, "std_3d": 480.6, "cv": 1.25},
                ]
            }
        }


@app.get("/api/anomalies/all-clicks")
def get_all_clicks(media: str = Query(None)):
    """
    Returns all clicks by media source, date and hour.
    
    Returns:
        dict: Status, number of records, and click data
    """
    try:
        if media == "partner":
            sql = """
                SELECT partner as media_source, event_date, event_hour, total_clicks
                FROM `practicode-2025.clicks_data_prac.partner_anomaly_all_clicks`
                ORDER BY event_date, event_hour, media_source
            """
        else:
            sql = """
                SELECT media_source, event_date, event_hour, total_clicks
                FROM `practicode-2025.clicks_data_prac.media_source_anomaly_all_clicks`
                ORDER BY event_date, event_hour, media_source
            """
        rows = bq_client.execute_query(sql, "all_clicks")
        data = [dict(row.items()) for row in rows]
        # Group by media_source or partner for level2
        grouped = {}
        key_name = "media_source"
        for item in data:
            key = item[key_name]
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(item)
        return {"status": "success", "count": len(data), "data": data, "level2": grouped}
    except Exception as e:
        logging.error(f"Error in get_all_clicks: {e}")
        # Return mock data if BigQuery fails - 72 data points per media source (3 days x 24 hours)
        mock_data = []
        media_sources = ["tiktok_int", "facebook_int", "google_int"]
        base_clicks = {"tiktok_int": 800, "facebook_int": 1200, "google_int": 950}
        for media in media_sources:
            for day in range(3):
                for hour in range(24):
                    # Simulate realistic click patterns with variation
                    import random
                    variation = random.randint(-200, 300)
                    clicks = base_clicks[media] + variation + (hour * 10)  # Peak during mid-day
                    mock_data.append({
                        "media_source": media,
                        "event_date": f"2024-12-{20+day}",
                        "event_hour": hour,
                        "total_clicks": max(100, clicks)  # Minimum 100 clicks
                    })
        # Group by media_source for level2
        grouped = {}
        for item in mock_data:
            media = item["media_source"]
            if media not in grouped:
                grouped[media] = []
            grouped[media].append(item)
        return {
            "status": "success",
            "count": len(mock_data),
            "data": mock_data,
            "level2": grouped
        }


@app.get("/api/anomalies/app-breakdown")
def get_app_breakdown(media: str = Query(None)):
    """
    Returns application breakdown by media source, date and hour.
    
    Returns:
        dict: Status and application data grouped by key
    """
    try:
        if media == "partner":
            sql = """
                SELECT partner, event_date, event_hour, app_id, total_clicks
                FROM `practicode-2025.clicks_data_prac.partner_anomaly_media_source_app_root_cause`
                ORDER BY partner, event_date, event_hour, app_id
            """
        
        else:
            sql = """
                SELECT media_source, event_date, event_hour, app_id, total_clicks
                FROM `practicode-2025.clicks_data_prac.media_source_anomaly_app_root_cause`
                ORDER BY media_source, event_date, event_hour, app_id
            """
        rows = bq_client.execute_query(sql, "app_breakdown")
        data = [dict(row.items()) for row in rows]
        # Group by media_source/partner + event_date + event_hour for level3
        app_grouped = {}
        key_name = "partner" if media == "partner" else "media_source"
        for item in data:
            key = f"{item[key_name]}_{item['event_date']}_{item['event_hour']}"
            if key not in app_grouped:
                app_grouped[key] = []
            app_grouped[key].append(item)
        return {"status": "success", "count": len(data), "level3": app_grouped}
    except Exception as e:
        logging.error(f"Error in get_app_breakdown: {e}")
        return {"status": "error", "message": str(e), "level3": {}}
