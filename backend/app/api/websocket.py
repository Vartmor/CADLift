"""
WebSocket endpoint for real-time job updates.

This module provides WebSocket support for:
- Real-time job status updates
- Progress tracking
- Error notifications
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.logging import get_logger

logger = get_logger("cadlift.websocket")

router = APIRouter(prefix="/ws", tags=["websocket"])


class ConnectionManager:
    """Manages WebSocket connections and job subscriptions."""

    def __init__(self):
        # Map of job_id -> set of connected websockets
        self.job_subscriptions: Dict[str, Set[WebSocket]] = {}
        # Map of websocket -> set of subscribed job_ids
        self.websocket_subscriptions: Dict[WebSocket, Set[str]] = {}
        # All active connections
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        self.websocket_subscriptions[websocket] = set()
        logger.info("WebSocket connected", extra={"total_connections": len(self.active_connections)})

    def disconnect(self, websocket: WebSocket):
        """Handle WebSocket disconnection and cleanup subscriptions."""
        self.active_connections.discard(websocket)
        
        # Clean up job subscriptions for this websocket
        if websocket in self.websocket_subscriptions:
            for job_id in self.websocket_subscriptions[websocket]:
                if job_id in self.job_subscriptions:
                    self.job_subscriptions[job_id].discard(websocket)
                    if not self.job_subscriptions[job_id]:
                        del self.job_subscriptions[job_id]
            del self.websocket_subscriptions[websocket]
        
        logger.info("WebSocket disconnected", extra={"total_connections": len(self.active_connections)})

    def subscribe_to_job(self, websocket: WebSocket, job_id: str):
        """Subscribe a websocket to job updates."""
        if job_id not in self.job_subscriptions:
            self.job_subscriptions[job_id] = set()
        self.job_subscriptions[job_id].add(websocket)
        
        if websocket in self.websocket_subscriptions:
            self.websocket_subscriptions[websocket].add(job_id)
        
        logger.debug("Subscribed to job", extra={"job_id": job_id})

    def unsubscribe_from_job(self, websocket: WebSocket, job_id: str):
        """Unsubscribe a websocket from job updates."""
        if job_id in self.job_subscriptions:
            self.job_subscriptions[job_id].discard(websocket)
            if not self.job_subscriptions[job_id]:
                del self.job_subscriptions[job_id]
        
        if websocket in self.websocket_subscriptions:
            self.websocket_subscriptions[websocket].discard(job_id)

    async def send_job_update(self, job_id: str, data: dict):
        """Send update to all websockets subscribed to a job."""
        if job_id not in self.job_subscriptions:
            return
        
        message = json.dumps({
            "type": "job_update",
            "job_id": job_id,
            **data
        })
        
        disconnected = []
        for websocket in self.job_subscriptions[job_id]:
            try:
                await websocket.send_text(message)
            except Exception:
                disconnected.append(websocket)
        
        # Clean up disconnected websockets
        for ws in disconnected:
            self.disconnect(ws)

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected websockets."""
        text = json.dumps(message)
        disconnected = []
        
        for websocket in self.active_connections:
            try:
                await websocket.send_text(text)
            except Exception:
                disconnected.append(websocket)
        
        for ws in disconnected:
            self.disconnect(ws)


# Global connection manager instance
manager = ConnectionManager()


@router.websocket("/jobs")
async def websocket_jobs_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for job updates.
    
    Messages from client:
    - {"type": "subscribe", "job_id": "<id>"} - Subscribe to job updates
    - {"type": "unsubscribe", "job_id": "<id>"} - Unsubscribe from job updates
    - {"type": "ping"} - Keepalive ping
    
    Messages to client:
    - {"type": "job_update", "job_id": "<id>", "status": "...", "progress": 0-100}
    - {"type": "job_completed", "job_id": "<id>", "data": {...}}
    - {"type": "job_failed", "job_id": "<id>", "error": "..."}
    - {"type": "pong"} - Response to ping
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                msg_type = message.get("type")
                
                if msg_type == "subscribe":
                    job_id = message.get("job_id")
                    if job_id:
                        manager.subscribe_to_job(websocket, job_id)
                        await websocket.send_text(json.dumps({
                            "type": "subscribed",
                            "job_id": job_id
                        }))
                
                elif msg_type == "unsubscribe":
                    job_id = message.get("job_id")
                    if job_id:
                        manager.unsubscribe_from_job(websocket, job_id)
                        await websocket.send_text(json.dumps({
                            "type": "unsubscribed",
                            "job_id": job_id
                        }))
                
                elif msg_type == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                
                else:
                    logger.warning("Unknown WebSocket message type", extra={"type": msg_type})
            
            except json.JSONDecodeError:
                logger.warning("Invalid JSON in WebSocket message")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON"
                }))
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error("WebSocket error", extra={"error": str(e)})
        manager.disconnect(websocket)


# Helper function for other modules to send job updates
async def notify_job_update(job_id: str, status: str, progress: int = 0, **extra):
    """
    Send a job update notification to all subscribed clients.
    
    Args:
        job_id: The job ID
        status: Current job status
        progress: Progress percentage (0-100)
        **extra: Additional data to include in the message
    """
    await manager.send_job_update(job_id, {
        "status": status,
        "progress": progress,
        **extra
    })


async def notify_job_completed(job_id: str, data: dict = None):
    """Send a job completion notification."""
    await manager.send_job_update(job_id, {
        "type": "job_completed",
        "status": "completed",
        "progress": 100,
        "data": data or {}
    })


async def notify_job_failed(job_id: str, error: str):
    """Send a job failure notification."""
    await manager.send_job_update(job_id, {
        "type": "job_failed",
        "status": "failed",
        "error": error
    })
