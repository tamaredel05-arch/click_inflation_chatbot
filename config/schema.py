SQL_SCHEMA = {
    "table_name": "clicks_data_prac.partial_encoded_clicks",
    "description": "Processed click/view events used for fraud detection and traffic-quality analysis.",
    "fields": {

        "_rid": {
            "type": "STRING",
            "description": "Unique row identifier (UUID). Internal use only."
        },

        "event_time": {
            "type": "TIMESTAMP",
            "description": "Timestamp when the event occurred (UTC). Used for attribution windowing and event sequencing."
        },

        "hr": {
            "type": "INTEGER",
            "description": "Hour of the day (0–23). Helps detect unusual hourly activity patterns."
        },

        "is_engaged_view": {
            "type": "BOOLEAN",
            "description": "TRUE = view only, FALSE = real click. Important for detecting fraudulent clicks."
        },

        "is_retargeting": {
            "type": "BOOLEAN",
            "description": "Indicates if the event belongs to a retargeting campaign. TRUE = previous installer."
        },

        "media_source": {
            "type": "STRING",
            "description": "The entity behind the advertisement (media network/source)."
        },

        "partner": {
            "type": "STRING",
            "description": "Ad partner/agency acting as the intermediary between the advertiser and the media source."
        },

        "app_id": {
            "type": "STRING",
            "description": "Identifier of the advertised application, published via the source id."
        },

        "site_id": {
            "type": "STRING",
            "description": "The platform/app where the ad was displayed (the publishing source)."
        },

        "engagement_type": {
            "type": "STRING",
            "description": "Type of interaction: click, view, engaged_view, or other event type."
        },

        "total_events": {
            "type": "INTEGER",
            "description": "Number of identical events aggregated into one row. Helps detect suspicious spikes."
        }
    }
}

